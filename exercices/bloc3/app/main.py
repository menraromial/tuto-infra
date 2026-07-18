"""API minimale qui interroge PostgreSQL (exercice final du bloc 3)."""
import os

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)

DSN = (
    f"host={os.environ['DB_HOST']} "
    f"port={os.environ.get('DB_PORT', '5432')} "
    f"dbname={os.environ['DB_NAME']} "
    f"user={os.environ['DB_USER']} "
    f"password={os.environ['DB_PASSWORD']}"
)


@app.get("/")
def index():
    with psycopg.connect(DSN, connect_timeout=3) as conn:
        version = conn.execute("SELECT version()").fetchone()[0]
    return jsonify(message="Les deux services communiquent !", postgres=version)


@app.get("/healthz")
def healthz():
    """Liveness : le processus répond (ne dépend pas de la base)."""
    return jsonify(status="ok")


@app.get("/ready")
def ready():
    """Readiness : la base est joignable."""
    with psycopg.connect(DSN, connect_timeout=3) as conn:
        conn.execute("SELECT 1")
    return jsonify(status="ready")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
