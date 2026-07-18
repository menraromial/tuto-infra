"""Producer de l'exercice final du bloc 6 : envoie des commandes JSON dans Kafka.

Usage : python producer.py [--nombre 500]
"""
import argparse
import json
import random
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

BROKERS = "localhost:19092"
TOPIC = "commandes"

PRODUITS = [
    ("clavier", 49.90),
    ("souris", 19.90),
    ("ecran", 179.00),
    ("casque", 89.50),
    ("webcam", 59.00),
    ("dock-usb", 129.00),
]


def fabrique_evenement() -> dict:
    produit, prix = random.choice(PRODUITS)
    return {
        # Identifiant unique de l'évènement : c'est la clé de déduplication
        # qui permet à l'aval de rester idempotent malgré les doublons.
        "event_id": str(uuid.uuid4()),
        "client_id": f"c{random.randint(1, 5):03d}",
        "produit": produit,
        "quantite": random.randint(1, 5),
        "prix_unitaire": prix,
        "horodatage": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nombre", type=int, default=500)
    args = parser.parse_args()

    producer = Producer({"bootstrap.servers": BROKERS})
    compteur = {"ok": 0}

    def accuse_reception(err, msg):
        if err is not None:
            print(f"échec d'envoi : {err}")
        else:
            compteur["ok"] += 1

    for _ in range(args.nombre):
        evt = fabrique_evenement()
        producer.produce(
            TOPIC,
            # La clé décide de la partition : un même client va toujours sur la
            # même partition, donc ses évènements restent ordonnés entre eux.
            key=evt["client_id"],
            value=json.dumps(evt).encode(),
            callback=accuse_reception,
        )
        producer.poll(0)  # traite les accusés de réception au fil de l'eau

    producer.flush()  # attend que tout soit réellement écrit dans le broker
    print(f"{compteur['ok']}/{args.nombre} évènements produits dans '{TOPIC}'")


if __name__ == "__main__":
    main()
