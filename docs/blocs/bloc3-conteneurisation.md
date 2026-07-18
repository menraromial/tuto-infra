# Bloc 3 : Conteneurisation avec Podman puis Kubernetes (kind)

Objectif du bloc : maîtriser les conteneurs avec **Podman**, puis déployer sur un
cluster Kubernetes local créé avec **kind**. Tout ce qui suit a été testé sur
Podman 5.x rootless (sans droits root).

!!! note "Pourquoi Podman et pas Docker ?"
    Podman expose la même ligne de commande et la même API que Docker
    (`podman run` ≡ `docker run`), mais fonctionne **sans démon central et sans
    root** : chaque conteneur est un simple processus de ton utilisateur.
    Tout tutoriel Docker s'applique donc tel quel : remplace juste `docker`
    par `podman`.

## 1. Installer et vérifier Podman

```bash
# Debian / Ubuntu / WSL2
sudo apt install podman

# Vérifications
podman --version
podman info --format '{{.Host.Security.Rootless}} {{.Store.GraphDriverName}}'
```

Sortie attendue de la deuxième commande : `true overlay` (mode rootless, pilote
de stockage overlay).

Premier conteneur :

```bash
podman run --rm quay.io/podman/hello
```

## 2. Activer la socket API (indispensable pour compose et le bloc 4)

Certains outils (docker-compose, le runner CI du bloc 4, kind) parlent à Podman
via une socket compatible Docker. On l'active une fois pour toutes :

```bash
systemctl --user enable --now podman.socket

# Vérification : doit répondre "OK"
curl -s --unix-socket $XDG_RUNTIME_DIR/podman/podman.sock http://d/_ping
```

## 3. `podman compose` : stacks multi-services

`podman compose` délègue à un provider (docker-compose ou podman-compose) en
pointant automatiquement vers la socket Podman :

```bash
podman compose version
```

Tous les fichiers `compose.yaml` des blocs suivants se lancent avec
`podman compose up -d` depuis leur dossier.

## 4. Kubernetes local avec kind

!!! info "Pourquoi kind et pas minikube ?"
    - **kind** (*Kubernetes in Docker*) crée le cluster dans de simples
      conteneurs : pas de VM, création en ~1 minute, destruction instantanée.
    - C'est l'outil officiel du projet Kubernetes (SIG Testing) et il
      fonctionne bien avec **Podman rootless**, alors que le driver Podman de minikube
      est encore expérimental et fragile en rootless.
    - Le cluster est défini par un **fichier YAML versionné dans le dépôt** :
      tout le monde reproduit exactement le même environnement.

    Si tu es sous Docker Desktop, minikube fonctionne bien aussi ; les
    manifests Kubernetes de ce parcours restent identiques.

### Installation de kubectl, helm et kind

```bash
# kubectl : https://kubernetes.io/fr/docs/tasks/tools/
# helm    : https://helm.sh/fr/docs/intro/install/

# kind (binaire unique, version stable la plus récente)
VER=$(curl -s https://api.github.com/repos/kubernetes-sigs/kind/releases/latest \
      | grep -oP '"tag_name": "\K[^"]+')
curl -sLo ~/.local/bin/kind \
  "https://github.com/kubernetes-sigs/kind/releases/download/$VER/kind-linux-amd64"
chmod +x ~/.local/bin/kind
kind version
```

!!! warning "Prérequis rootless : cgroups v2 délégués"
    Vérifie que les contrôleurs `cpu memory pids` apparaissent dans :
    ```bash
    cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers
    ```
    C'est le cas par défaut sur les distributions récentes (systemd ≥ 244).

### Réglages système (une fois par machine)

Deux réglages de l'hôte sont nécessaires : les limites inotify du noyau (trop
basses par défaut pour un cluster Kubernetes, symptôme : des pods qui crashent
avec `too many open files`) et la résolution du nom `gitea` (utilisé au
bloc 4). Un script idempotent et commenté fait les deux :

```bash
sudo bash scripts/setup-hote.sh
```

### Création du cluster

Le cluster est décrit dans [`infra/kind/cluster.yaml`](https://github.com/menraromial/tuto-infra/blob/main/infra/kind/cluster.yaml) :
un nœud unique, deux mappings de ports (NodePort 30080 → `localhost:8088` pour
ce bloc, 30081 → `localhost:8089` pour le bloc 4) et un patch containerd qui
prépare l'accès au registre d'images local du bloc 4.

```bash
bash infra/kind/create-cluster.sh
```

Le script (court, lis-le !) exécute `kind create cluster --config cluster.yaml`
puis autorise le registre HTTP `gitea:3000` auprès du containerd du nœud.
La variable `KIND_EXPERIMENTAL_PROVIDER=podman` qu'il exporte force l'usage de
Podman (sinon kind cherche Docker) ; ajoute
`export KIND_EXPERIMENTAL_PROVIDER=podman` dans ton `~/.bashrc` ou `~/.zshrc`
pour tes propres commandes kind.

Vérification :

```bash
kubectl --context kind-tuto get nodes
# NAME                 STATUS   ROLES           AGE   VERSION
# tuto-control-plane   Ready    control-plane   1m    v1.36.x
```

### Smoke test : un déploiement de bout en bout

```bash
kubectl create deployment smoke --image=nginx:alpine
kubectl expose deployment smoke --type=NodePort --port=80 \
  --overrides='{"spec":{"ports":[{"port":80,"nodePort":30080}]}}'
kubectl rollout status deployment/smoke

curl -s http://localhost:8088/ | grep '<title>'
# <title>Welcome to nginx!</title>
```

Si tu vois le titre nginx : ton cluster fonctionne de bout en bout
(pod → service NodePort → mapping de port kind → ta machine). Nettoyage :

```bash
kubectl delete deployment smoke && kubectl delete service smoke
```

Pour détruire et recréer le cluster à volonté :

```bash
kind delete cluster --name tuto
```

## Dépannage

??? failure "`Cannot connect to the Docker daemon at unix://…/podman/podman.sock`"
    La socket Podman n'existe plus (elle disparaît parfois après un
    redémarrage ou un nettoyage de `/run`). Relance-la :
    ```bash
    systemctl --user restart podman.socket
    curl -s --unix-socket $XDG_RUNTIME_DIR/podman/podman.sock http://d/_ping
    ```

??? failure "Pull d'image en `403 Forbidden` alors que le registre est public"
    Des identifiants périmés sont probablement stockés pour ce registre
    (`~/.docker/config.json` ou `~/.config/containers/auth.json`). Vérifie et
    supprime-les :
    ```bash
    podman logout --authfile ~/.docker/config.json ghcr.io
    ```

## Exercice final du bloc

Déployer une stack de deux services qui communiquent (une API Flask et sa
base PostgreSQL) avec ConfigMap, Secret et probes. La solution complète est
dans [`exercices/bloc3/`](https://github.com/menraromial/tuto-infra/tree/main/exercices/bloc3) :

```
exercices/bloc3/
├── app/            # code de l'API + Dockerfile multi-stage
└── k8s/            # manifests : namespace, postgres, api
```

### 1. Construire l'image et la charger dans kind

Le cluster ne voit pas les images de ton Podman : il faut les lui transférer.

```bash
cd exercices/bloc3/app
podman build -t bloc3-api:v1 .

podman save -o /tmp/bloc3-api.tar localhost/bloc3-api:v1
KIND_EXPERIMENTAL_PROVIDER=podman kind load image-archive /tmp/bloc3-api.tar --name tuto
```

!!! bug "Pourquoi pas `kind load docker-image` ?"
    Avec le provider Podman, `kind load docker-image` échoue souvent avec
    `image not present locally` (résolution du préfixe `localhost/`). Le
    passage par une archive `podman save` fonctionne dans tous les cas.
    C'est aussi pour ça que le Deployment utilise `imagePullPolicy: Never` :
    l'image est déjà sur le nœud, il ne faut surtout pas la chercher sur un
    registre.

### 2. Déployer et vérifier

```bash
kubectl apply -f exercices/bloc3/k8s/
kubectl -n bloc3 get pods          # attendre 2 api + 1 postgres en Running

curl -s http://localhost:8088/
# {"message":"Les deux services communiquent !","postgres":"PostgreSQL 17.x ..."}
```

L'API lit sa configuration dans un ConfigMap (`DB_HOST: postgres`, le nom du
**Service**, résolu par le DNS interne du cluster) et le mot de passe dans le
Secret partagé avec PostgreSQL.

### 3. Tester l'auto-guérison

```bash
kubectl -n bloc3 delete pod -l app=api
kubectl -n bloc3 get pods -l app=api    # de nouveaux pods remplacent les anciens
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8088/   # 200 pendant le remplacement
```

Le Deployment (via son ReplicaSet) maintient le nombre de réplicas : détruire
les pods déclenche leur recréation, et avec 2 réplicas le service ne tombe
jamais. C'est exactement le contrat de Kubernetes : tu déclares l'état voulu,
il le maintient.

**Critères de réussite** : `curl localhost:8088` renvoie la version de
PostgreSQL (les deux services communiquent), et la suppression des pods API ne
coupe pas le service.
