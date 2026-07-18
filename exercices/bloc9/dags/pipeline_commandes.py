"""DAG de l'exercice final du bloc 9 : orchestre le pipeline des blocs 6-7.

Chaîne quotidienne :
    archiver_kafka  ->  deposer_bronze  ->  dbt_run  ->  dbt_test

Chaque tâche est idempotente : le DAG entier peut être rejoué sans dégât
(voir le cours, sections idempotence et backfill).
"""
from __future__ import annotations

import os
from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

EXERCICES = "/opt/exercices"


def deposer_bronze() -> None:
    """Dépose les Parquet locaux dans la couche bronze de MinIO.

    Ré-écrire un objet au même chemin est sans effet : la tâche est
    idempotente, la rejouer ne crée jamais de doublon d'objet.
    """
    from pathlib import Path

    from minio import Minio

    client = Minio(
        os.environ["S3_ENDPOINT"],
        access_key="minio",
        secret_key="minio12345",
        secure=False,
    )
    fichiers = sorted(Path(EXERCICES, "bloc6", "data").glob("*.parquet"))
    for fichier in fichiers:
        client.fput_object("lake", f"bronze/commandes/{fichier.name}", str(fichier))
    print(f"{len(fichiers)} fichiers présents dans le bronze")


with DAG(
    dag_id="pipeline_commandes",
    description="Ingestion Kafka -> bronze MinIO -> transformations dbt",
    schedule="@daily",                                   # un run par jour
    start_date=pendulum.datetime(2026, 7, 14, tz="UTC"),
    catchup=False,                                       # pas de rattrapage auto du passé
    default_args={
        "retries": 2,                                    # 2 nouvelles tentatives...
        "retry_delay": timedelta(minutes=1),             # ...à 1 minute d'intervalle
    },
    doc_md=__doc__,
    tags=["tuto", "bloc9"],
) as dag:

    archiver_kafka = BashOperator(
        task_id="archiver_kafka",
        bash_command=(
            f"cd {EXERCICES}/bloc6 && python consumer_parquet.py --lot 200"
        ),
    )

    bronze = PythonOperator(
        task_id="deposer_bronze",
        python_callable=deposer_bronze,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"cd {EXERCICES}/bloc7 && "
            f"DBT_PROFILES_DIR={EXERCICES}/bloc7 dbt run --no-use-colors"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {EXERCICES}/bloc7 && "
            f"DBT_PROFILES_DIR={EXERCICES}/bloc7 dbt test --no-use-colors"
        ),
    )

    # Les dépendances : c'est CETTE ligne qui dessine le DAG.
    archiver_kafka >> bronze >> dbt_run >> dbt_test
