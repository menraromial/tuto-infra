#!/usr/bin/env bash
# Crée les deux conteneurs "serveurs" que le playbook va configurer.
# Chacun sert /srv/www en HTTP : srv1 sur localhost:8081, srv2 sur localhost:8082.
set -euo pipefail

for i in 1 2; do
  name="srv$i"
  port=$((8080 + i))
  if podman container exists "$name" 2>/dev/null; then
    echo ">> $name existe déjà (http://localhost:${port})"
    continue
  fi
  # "--bind ::" fait écouter le serveur en IPv6 ET IPv4 (dual-stack) :
  # sans ça, "localhost" (souvent résolu en ::1) donne connexion réinitialisée.
  podman run -d --name "$name" -p "${port}:8080" docker.io/library/python:3.12-slim \
    sh -c 'mkdir -p /srv/www && echo "en attente de configuration" > /srv/www/index.html && exec python -m http.server 8080 --bind :: --directory /srv/www' \
    > /dev/null
  echo ">> $name créé (http://localhost:${port})"
done
