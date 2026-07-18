"""Porte de qualité et promotion du modèle (bloc 11).

Compare la dernière version enregistrée du modèle au champion en place :
    - AUC >= seuil absolu (un mauvais modèle ne part JAMAIS en production)
    - AUC >= AUC du champion actuel (on ne régresse pas)
Si les deux conditions passent, la nouvelle version reçoit l'alias
"champion" ; sinon, on ne touche à rien et on le dit.

Un refus n'est pas une erreur : le script sort alors avec le code 99, que
le BashOperator d'Airflow interprète comme "tâche à sauter" (skipped),
et le rechargement de l'application n'a pas lieu.

Usage : python promouvoir.py [--seuil-auc 0.9]
"""
import argparse
import os
import sys

import mlflow
from mlflow import MlflowClient

MODELE = "score-risque"
CODE_REFUS = 99  # skip_on_exit_code par défaut du BashOperator


def auc_de(client: MlflowClient, version) -> float:
    run = client.get_run(version.run_id)
    return run.data.metrics.get("auc", 0.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seuil-auc", type=float, default=0.90)
    args = parser.parse_args()

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5002"))
    client = MlflowClient()

    versions = client.search_model_versions(f"name = '{MODELE}'")
    candidate = max(versions, key=lambda v: int(v.version))
    auc_candidat = auc_de(client, candidate)
    print(f"candidat : version {candidate.version}, auc={auc_candidat:.4f}")

    # Porte 1 : le seuil absolu.
    if auc_candidat < args.seuil_auc:
        print(f"REFUS : auc {auc_candidat:.4f} < seuil {args.seuil_auc} : le champion reste en place.")
        sys.exit(CODE_REFUS)

    # Porte 2 : ne pas régresser face au champion actuel (s'il existe).
    try:
        champion = client.get_model_version_by_alias(MODELE, "champion")
        auc_champion = auc_de(client, champion)
        print(f"champion : version {champion.version}, auc={auc_champion:.4f}")
        if auc_candidat < auc_champion:
            print(f"REFUS : le candidat ({auc_candidat:.4f}) est moins bon que le champion ({auc_champion:.4f}).")
            sys.exit(CODE_REFUS)
    except mlflow.exceptions.RestException:
        print("aucun champion en place : première promotion")

    client.set_registered_model_alias(MODELE, "champion", candidate.version)
    print(f"PROMU : la version {candidate.version} est le nouveau champion")


if __name__ == "__main__":
    main()
