"""DAG de ré-entraînement du modèle de score de risque (bloc 11).

Chaîne quotidienne :
    construire_features -> entrainer -> porte_qualite_promotion -> recharger_app

La porte de qualité (promouvoir.py) sort avec le code 99 quand le candidat
ne mérite pas la promotion : la tâche passe en "skipped" (pas en échec,
un refus n'est pas un incident) et le rechargement n'a pas lieu.
"""
from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

EXERCICES = "/opt/exercices"

with DAG(
    dag_id="entrainement_score_risque",
    description="Features dbt -> entraînement -> porte de qualité -> rechargement de l'app",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 7, 14, tz="UTC"),
    catchup=False,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    doc_md=__doc__,
    tags=["tuto", "bloc11", "ml"],
) as dag:

    construire_features = BashOperator(
        task_id="construire_features",
        bash_command=(
            f"cd {EXERCICES}/bloc7 && "
            f"DBT_PROFILES_DIR={EXERCICES}/bloc7 dbt run --no-use-colors && "
            f"DBT_PROFILES_DIR={EXERCICES}/bloc7 dbt test --no-use-colors"
        ),
    )

    entrainer = BashOperator(
        task_id="entrainer",
        bash_command=f"python {EXERCICES}/bloc11/entrainement/train.py",
    )

    porte_qualite_promotion = BashOperator(
        task_id="porte_qualite_promotion",
        bash_command=f"python {EXERCICES}/bloc11/entrainement/promouvoir.py --seuil-auc 0.9",
        # exit 99 = refus de promotion = tâche "skipped" (comportement par
        # défaut de skip_on_exit_code, rendu explicite ici) :
        skip_on_exit_code=99,
    )

    recharger_app = BashOperator(
        task_id="recharger_app",
        # L'app tourne dans le cluster kind : on la joint via le NodePort
        # du nœud (le scheduler est attaché au réseau "kind").
        bash_command="curl -fsS -X POST http://tuto-control-plane:30080/recharger",
    )

    construire_features >> entrainer >> porte_qualite_promotion >> recharger_app
