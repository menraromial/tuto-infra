"""Application web de score de risque (exercice final du bloc 11).

Sert le modèle "champion" du registre MLflow :
    - GET  /          : formulaire de saisie d'une commande
    - POST /predire   : score de risque d'une commande (JSON)
    - POST /recharger : recharge le champion depuis MLflow (sans redéploiement)
    - GET  /sante     : état + version du modèle chargé
    - GET  /metrics   : métriques Prometheus (bloc 10)
"""
import os
import time

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from mlflow import MlflowClient
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel

MODELE = "score-risque"
SEUIL_VERDICT = 0.5

# Le prix "catalogue" de référence, le même que le producer du bloc 6.
CATALOGUE = {
    "clavier": 49.90, "souris": 19.90, "ecran": 179.00,
    "casque": 89.50, "webcam": 59.00, "dock-usb": 129.00,
}

PREDICTIONS = Counter("app_predictions_total", "Prédictions servies", ["verdict"])
SCORES = Histogram("app_score_risque", "Distribution des scores prédits",
                   buckets=[0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
LATENCE = Histogram("app_latence_prediction_secondes", "Latence de prédiction")

app = FastAPI(title="Score de risque")
etat = {"modele": None, "version": "aucun"}


def charge_champion() -> None:
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5002"))
    etat["modele"] = mlflow.sklearn.load_model(f"models:/{MODELE}@champion")
    version = MlflowClient().get_model_version_by_alias(MODELE, "champion")
    etat["version"] = version.version


@app.on_event("startup")
def demarre() -> None:
    charge_champion()


class Commande(BaseModel):
    produit: str
    quantite: int
    prix_unitaire: float
    commandes_client_jour: int = 1


@app.post("/predire")
def predire(commande: Commande) -> dict:
    if commande.produit not in CATALOGUE:
        raise HTTPException(422, f"produit inconnu : {commande.produit}")
    debut = time.monotonic()
    features = pd.DataFrame([{
        "quantite": commande.quantite,
        "montant": commande.quantite * commande.prix_unitaire,
        "ratio_prix": commande.prix_unitaire / CATALOGUE[commande.produit],
        "commandes_client_jour": commande.commandes_client_jour,
    }])
    score = float(etat["modele"].predict_proba(features)[0, 1])
    verdict = "suspecte" if score >= SEUIL_VERDICT else "normale"
    LATENCE.observe(time.monotonic() - debut)
    SCORES.observe(score)
    PREDICTIONS.labels(verdict=verdict).inc()
    return {"score": round(score, 4), "verdict": verdict, "version_modele": etat["version"]}


@app.post("/recharger")
def recharger() -> dict:
    charge_champion()
    return {"rechargé": True, "version_modele": etat["version"]}


@app.get("/sante")
def sante() -> dict:
    return {"statut": "ok", "version_modele": etat["version"]}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
def accueil() -> str:
    options = "".join(f'<option value="{p}">{p} ({v:.2f})</option>' for p, v in CATALOGUE.items())
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Score de risque</title>
<style>
 body {{ font-family: sans-serif; max-width: 30rem; margin: 3rem auto; }}
 label {{ display: block; margin-top: .8rem; }}
 input, select {{ width: 100%; padding: .4rem; }}
 button {{ margin-top: 1rem; padding: .6rem 1.2rem; }}
 #resultat {{ margin-top: 1.5rem; padding: 1rem; border-radius: .5rem; display: none; }}
 .normale {{ background: #e6f4e6; }} .suspecte {{ background: #fbe3e3; }}
</style></head><body>
<h1>Score de risque de commande</h1>
<p>Modèle champion v{etat["version"]}, servi depuis le registre MLflow.</p>
<label>Produit <select id="produit">{options}</select></label>
<label>Quantité <input id="quantite" type="number" value="2" min="1"></label>
<label>Prix unitaire <input id="prix" type="number" step="0.01" value="49.90"></label>
<label>Commandes de ce client aujourd'hui <input id="cmdjour" type="number" value="1" min="1"></label>
<button onclick="predire()">Évaluer la commande</button>
<div id="resultat"></div>
<script>
async function predire() {{
  const corps = {{
    produit: document.getElementById('produit').value,
    quantite: +document.getElementById('quantite').value,
    prix_unitaire: +document.getElementById('prix').value,
    commandes_client_jour: +document.getElementById('cmdjour').value,
  }};
  const rep = await fetch('/predire', {{method:'POST',
    headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(corps)}});
  const r = await rep.json();
  const div = document.getElementById('resultat');
  div.className = r.verdict; div.style.display = 'block';
  div.textContent = `Commande ${{r.verdict.toUpperCase()}} : score de risque ${{(r.score*100).toFixed(1)}} % (modèle v${{r.version_modele}})`;
}}
</script></body></html>"""
