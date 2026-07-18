"""Application témoin du pipeline CI/CD GitOps (exercice final du bloc 4)."""
import os

from flask import Flask, jsonify

app = Flask(__name__)

# Injecté au build de l'image (ARG GIT_SHA) : permet de voir quelle
# version du code tourne réellement dans le cluster.
VERSION = os.environ.get("GIT_SHA", "dev")


@app.get("/")
def index():
    return jsonify(
        app="bloc4-app",
        version=VERSION,
        message="Déployé automatiquement par ArgoCD !",
    )


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
