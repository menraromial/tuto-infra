"""Entraînement du modèle de score de risque (bloc 11).

Lit les features préparées par dbt, entraîne une régression logistique,
évalue sur un découpage TEMPOREL, et enregistre le tout dans MLflow
(paramètres, métriques, modèle versionné).

Usage : python train.py [--warehouse ../bloc7/warehouse.duckdb]
"""
import argparse
import os

import duckdb
import mlflow
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["quantite", "montant", "ratio_prix", "commandes_client_jour"]
LABEL = "signalement_fraude"
MODELE = "score-risque"


def charge_features(chemin_warehouse: str) -> pd.DataFrame:
    # read_only : ne pose pas de verrou, dbt peut travailler à côté.
    with duckdb.connect(chemin_warehouse, read_only=True) as conn:
        return conn.execute(
            "SELECT * FROM features_commandes ORDER BY horodate_a"
        ).df()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--warehouse",
        default=os.path.join(os.path.dirname(__file__), "..", "..", "bloc7", "warehouse.duckdb"),
    )
    args = parser.parse_args()

    df = charge_features(args.warehouse)

    # Découpage TEMPOREL 80/20 : on s'évalue sur "le futur", jamais sur des
    # données mélangées, sinon le score est optimiste (fuite temporelle).
    coupure = int(len(df) * 0.8)
    train, test = df.iloc[:coupure], df.iloc[coupure:]

    modele = Pipeline([
        ("normalisation", StandardScaler()),
        # class_weight="balanced" : les fraudes sont rares (~5 %), sans ce
        # réglage le modèle apprendrait surtout à dire "tout va bien".
        ("regression", LogisticRegression(class_weight="balanced", max_iter=1000)),
    ])
    modele.fit(train[FEATURES], train[LABEL])

    scores = modele.predict_proba(test[FEATURES])[:, 1]
    predictions = scores >= 0.5
    auc = roc_auc_score(test[LABEL], scores)
    precision = precision_score(test[LABEL], predictions, zero_division=0)
    rappel = recall_score(test[LABEL], predictions, zero_division=0)

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5002"))
    mlflow.set_experiment(MODELE)
    with mlflow.start_run() as run:
        mlflow.log_params({
            "algo": "regression_logistique",
            "features": ",".join(FEATURES),
            "lignes_train": len(train),
            "lignes_test": len(test),
        })
        mlflow.log_metrics({"auc": auc, "precision": precision, "rappel": rappel})
        mlflow.sklearn.log_model(
            modele,
            name="modele",
            registered_model_name=MODELE,  # versionné dans le registre
        )
        print(f"run_id={run.info.run_id}")

    print(f"auc={auc:.4f} precision={precision:.4f} rappel={rappel:.4f}")


if __name__ == "__main__":
    main()
