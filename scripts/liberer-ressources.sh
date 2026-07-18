#!/usr/bin/env bash
# Libère les ressources de la plateforme du tutoriel (blocs 3 à 11).
#
#   bash scripts/liberer-ressources.sh          # PAUSE : arrête tout, garde les données
#   bash scripts/liberer-ressources.sh --tout   # REMISE À ZÉRO : supprime conteneurs,
#                                               # volumes, cluster, réseaux et images du tuto
#
# Ne touche à AUCUN conteneur, volume ou image étranger au tutoriel.
set -uo pipefail
cd "$(dirname "$0")/.."

STACKS="monitoring mlflow airflow gitea ingestion lake localstack"
# Conteneurs créés hors compose (exercice Ansible du bloc 5) :
CONTENEURS_LIBRES="srv1 srv2"
# Tout ce que le tuto peut avoir créé, pour les vérifications et le rattrapage :
MOTIF_TUTO='^(gitea|gitea-runner|redpanda|redpanda-console|minio|localstack|airflow-.*|prometheus|grafana|statsd-exporter|node-exporter|mlflow|ingestion-.*|srv[12]|tuto-control-plane)$'
RESEAUX_TUTO='^(gitea|kind|ingestion_default|lake_default|airflow_default|monitoring_default|mlflow_default|localstack_default)$'
IMAGES_TUTO="localhost/tuto-airflow:bloc9 localhost/tuto-mlflow:bloc11 localhost/bloc3-api:v1"

if [ "${1:-}" = "--tout" ]; then
  echo ">> REMISE À ZÉRO COMPLÈTE (conteneurs + volumes + cluster + images du tuto)"
  for s in $STACKS; do
    [ -f "infra/$s/compose.yaml" ] && podman compose -f "infra/$s/compose.yaml" down -v 2>/dev/null
  done
  podman rm -f $CONTENEURS_LIBRES 2>/dev/null
  KIND_EXPERIMENTAL_PROVIDER=podman kind delete cluster --name tuto 2>/dev/null

  # Rattrapage : une suppression échoue parfois (conmon capricieux) ; on
  # balaie ce qui correspond STRICTEMENT aux noms du tuto.
  podman ps -a --format '{{.Names}}' | grep -E "$MOTIF_TUTO" | xargs -r podman rm -f
  podman volume ls --format '{{.Name}}' \
    | grep -E '^(gitea|ingestion|lake|airflow|monitoring|mlflow|localstack)_' | xargs -r podman volume rm
  podman network ls --format '{{.Name}}' | grep -E "$RESEAUX_TUTO" | xargs -r podman network rm 2>/dev/null
  podman rmi $IMAGES_TUTO 2>/dev/null
  echo ">> Remise à zéro terminée. Tout est reconstructible : c'est le principe du parcours."
else
  echo ">> PAUSE : arrêt de tous les conteneurs du tuto (données conservées)"
  for s in $STACKS; do
    [ -f "infra/$s/compose.yaml" ] && podman compose -f "infra/$s/compose.yaml" stop 2>/dev/null
  done
  podman stop $CONTENEURS_LIBRES tuto-control-plane 2>/dev/null
  echo ">> Pause terminée. Reprise : podman compose up -d dans chaque dossier infra/,"
  echo "   et podman start tuto-control-plane pour le cluster."
fi

echo
echo ">> Conteneurs du tuto restants :"
podman ps -a --format '{{.Names}}\t{{.Status}}' | awk '{print $1}' | grep -E "$MOTIF_TUTO" || echo "   (aucun)"
