#!/usr/bin/env bash
# Crée (ou recrée) le cluster kind "tuto" sur Podman, puis autorise le
# registre HTTP de Gitea (gitea:3000) auprès du containerd du nœud.
set -euo pipefail
cd "$(dirname "$0")"

export KIND_EXPERIMENTAL_PROVIDER=podman

if kind get clusters 2>/dev/null | grep -qx tuto; then
  echo ">> Le cluster 'tuto' existe déjà. Pour le recréer :"
  echo "   kind delete cluster --name tuto && $0"
  exit 1
fi

kind create cluster --config cluster.yaml

# Podman copie le /etc/hosts de la machine dans le conteneur-nœud : si la
# machine associe "gitea" à 127.0.0.1 (bloc 4), le nœud essaierait de
# joindre le registre sur sa propre boucle locale. On retire l'entrée,
# le DNS du réseau kind donne la bonne adresse. (À refaire si le nœud
# redémarre : voir le dépannage du bloc 4.)
podman exec tuto-control-plane sh -c \
  "grep -v '127.0.0.1.gitea' /etc/hosts > /tmp/h && cat /tmp/h > /etc/hosts" || true

echo ">> Autorisation du registre HTTP gitea:3000 dans containerd..."
podman exec tuto-control-plane mkdir -p '/etc/containerd/certs.d/gitea:3000'
podman exec -i tuto-control-plane tee '/etc/containerd/certs.d/gitea:3000/hosts.toml' >/dev/null <<'EOF'
server = "http://gitea:3000"

[host."http://gitea:3000"]
  capabilities = ["pull", "resolve"]
  skip_verify = true
EOF

echo ">> Cluster prêt :"
kubectl --context kind-tuto get nodes
