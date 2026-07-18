#!/usr/bin/env bash
# Réglages système (une seule fois par machine) pour les blocs 3 et 4.
# Usage : sudo bash scripts/setup-hote.sh
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Lance ce script avec sudo : sudo bash $0" >&2
  exit 1
fi

# 1. Le nom "gitea" doit être résolu par la machine (registre d'images,
#    navigateur) : les conteneurs, eux, le résolvent via le réseau Podman.
if ! grep -q "127.0.0.1 gitea" /etc/hosts; then
  echo "127.0.0.1 gitea" >> /etc/hosts
  echo ">> /etc/hosts : entrée '127.0.0.1 gitea' ajoutée"
else
  echo ">> /etc/hosts : entrée déjà présente"
fi

# 2. Limites inotify : trop basses par défaut pour un cluster kind
#    (ArgoCD échoue avec "too many open files" sinon).
#    Réf : https://kind.sigs.k8s.io/docs/user/known-issues/#pod-errors-due-to-too-many-open-files
cat > /etc/sysctl.d/99-kind-inotify.conf <<'EOF'
fs.inotify.max_user_instances=512
fs.inotify.max_user_watches=524288
EOF
sysctl --system > /dev/null
echo ">> inotify : max_user_instances=$(sysctl -n fs.inotify.max_user_instances), max_user_watches=$(sysctl -n fs.inotify.max_user_watches)"

echo ">> Terminé."
