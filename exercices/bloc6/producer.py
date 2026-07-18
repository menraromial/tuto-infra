"""Producer de l'exercice final du bloc 6 : envoie des commandes JSON dans Kafka.

Usage : python producer.py [--nombre 500]
"""
import argparse
import json
import os
import random
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

# Surchargeable par variable d'environnement : depuis un conteneur (Airflow,
# bloc 9), le broker s'appelle "redpanda:9092" et non "localhost:19092".
BROKERS = os.environ.get("KAFKA_BROKERS", "localhost:19092")
TOPIC = "commandes"

PRODUITS = [
    ("clavier", 49.90),
    ("souris", 19.90),
    ("ecran", 179.00),
    ("casque", 89.50),
    ("webcam", 59.00),
    ("dock-usb", 129.00),
]


def fabrique_evenement(taux_anomalies: float = 0.0) -> dict:
    """Fabrique une commande normale, ou anormale avec probabilité donnée.

    Les anomalies (bloc 11) simulent des fraudes : quantité aberrante ou
    prix falsifié. Le champ signalement_fraude joue le rôle du signalement
    a posteriori (client, analyste) qui sert de label d'entraînement ;
    l'application de scoring ne le reçoit évidemment jamais en entrée.
    """
    produit, prix = random.choice(PRODUITS)
    quantite = random.randint(1, 5)
    fraude = random.random() < taux_anomalies
    if fraude:
        if random.random() < 0.5:
            quantite = random.randint(20, 60)          # razzia improbable
        else:
            prix = round(prix * random.uniform(0.03, 0.15), 2)  # prix cassé
    return {
        # Identifiant unique de l'évènement : c'est la clé de déduplication
        # qui permet à l'aval de rester idempotent malgré les doublons.
        "event_id": str(uuid.uuid4()),
        "client_id": f"c{random.randint(1, 5):03d}",
        "produit": produit,
        "quantite": quantite,
        "prix_unitaire": prix,
        "horodatage": datetime.now(timezone.utc).isoformat(),
        "signalement_fraude": fraude,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nombre", type=int, default=500)
    parser.add_argument("--anomalies", type=float, default=0.0,
                        help="proportion de commandes frauduleuses (bloc 11), ex: 0.05")
    args = parser.parse_args()

    producer = Producer({"bootstrap.servers": BROKERS})
    compteur = {"ok": 0}

    def accuse_reception(err, msg):
        if err is not None:
            print(f"échec d'envoi : {err}")
        else:
            compteur["ok"] += 1

    for _ in range(args.nombre):
        evt = fabrique_evenement(args.anomalies)
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
