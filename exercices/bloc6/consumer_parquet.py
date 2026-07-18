"""Consumer de l'exercice final du bloc 6 : archive le topic en fichiers Parquet.

Lit le topic par lots ; chaque lot devient un fichier Parquet dans data/.
S'arrête tout seul après quelques secondes sans nouveau message.

Usage : python consumer_parquet.py [--lot 200]
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from confluent_kafka import Consumer

BROKERS = "localhost:19092"
TOPIC = "commandes"
DOSSIER_SORTIE = Path(__file__).parent / "data"


def ecrit_lot(lot: list[dict], numero: int) -> Path:
    """Écrit un lot d'évènements dans un fichier Parquet horodaté.

    Le numéro de lot évite d'écraser un fichier si deux lots
    sont écrits dans la même seconde.
    """
    table = pa.Table.from_pylist(lot)
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    chemin = DOSSIER_SORTIE / f"commandes-{horodatage}-lot{numero:04d}-{len(lot)}evts.parquet"
    pq.write_table(table, chemin, compression="snappy")
    return chemin


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lot", type=int, default=200, help="taille max d'un lot")
    args = parser.parse_args()
    DOSSIER_SORTIE.mkdir(exist_ok=True)

    consumer = Consumer(
        {
            "bootstrap.servers": BROKERS,
            # Le groupe : Kafka y mémorise notre position (les offsets commités).
            "group.id": "archiveur-parquet",
            # Premier démarrage du groupe : commencer au début du topic.
            "auto.offset.reset": "earliest",
            # On commite NOUS-MÊMES, seulement après l'écriture du fichier :
            # sémantique "au moins une fois" (jamais de perte, doublons possibles).
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([TOPIC])

    lot: list[dict] = []
    total = 0
    silences = 0
    numero_lot = 0

    try:
        while True:
            message = consumer.poll(timeout=1.0)

            if message is None:
                silences += 1
                # Plus rien depuis 5 s : on vide le dernier lot et on s'arrête.
                if silences >= 5:
                    break
                continue
            if message.error():
                print(f"erreur kafka : {message.error()}")
                continue

            silences = 0
            # Ignore les messages non structurés (ex. : le test fait avec rpk)
            try:
                evt = json.loads(message.value())
            except json.JSONDecodeError:
                continue
            if not isinstance(evt, dict) or "event_id" not in evt:
                continue
            lot.append(evt)

            if len(lot) >= args.lot:
                numero_lot += 1
                chemin = ecrit_lot(lot, numero_lot)
                consumer.commit(asynchronous=False)  # après l'écriture !
                total += len(lot)
                print(f"écrit {chemin.name}")
                lot = []
    finally:
        if lot:
            numero_lot += 1
            chemin = ecrit_lot(lot, numero_lot)
            consumer.commit(asynchronous=False)
            total += len(lot)
            print(f"écrit {chemin.name}")
        consumer.close()

    print(f"terminé : {total} évènements archivés dans {DOSSIER_SORTIE}/")


if __name__ == "__main__":
    main()
