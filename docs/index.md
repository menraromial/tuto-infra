# Socle infrastructure & data engineering

Bienvenue ! Ce site accompagne un parcours pratique en 10 blocs pour construire,
**entièrement en local et sans carte bancaire**, une mini plateforme data complète :
conteneurs, Kubernetes, CI/CD, infrastructure as code, ingestion, lake/warehouse,
orchestration et monitoring.

## Comment fonctionne ce parcours

Ce site n'est pas qu'une lecture : chaque bloc se **pratique**. Tous les
fichiers nécessaires (compose, manifests Kubernetes, scripts, solutions des
exercices) sont déjà prêts dans un dépôt Git que tu clones une fois, puis
chaque page te fait exécuter et comprendre les commandes, étape par étape.
Chaque page se termine par un exercice final et une section dépannage avec les
erreurs réellement rencontrées.

## Mise en route (à faire une fois)

### 1. Vérifier les prérequis machine

- Linux natif ou WSL2 sous Windows, 8 Go de RAM minimum (16 Go confortable)
- `git` installé (`sudo apt install git`)
- Les autres outils (Podman, kubectl, helm, kind) s'installent au fil des
  blocs, chaque page donne les commandes.

### 2. Cloner le dépôt du parcours

```bash
git clone https://github.com/menraromial/tuto-infra.git
cd tuto-infra
```

!!! important "Toutes les commandes partent de la racine du dépôt"
    Sauf mention contraire, les commandes des pages de blocs s'exécutent
    depuis le dossier `tuto-infra/` que tu viens de cloner. Les chemins
    comme `infra/kind/create-cluster.sh` ou `exercices/bloc3/` sont relatifs
    à cette racine.

### 3. Repérer la structure du dépôt

```
tuto-infra/
├── docs/        # les pages de ce site
├── infra/       # l'infrastructure locale : cluster kind, stack Gitea, ArgoCD
├── exercices/   # les solutions des exercices finaux de chaque bloc
└── scripts/     # réglages de la machine hôte (à lancer une fois, voir bloc 3)
```

### 4. Suivre les blocs dans l'ordre

1. Les blocs 1 (terminal) et 2 (Git) du [plan du parcours](plan.md) se
   pratiquent sans infrastructure particulière : suis leurs ressources.
2. À partir du [bloc 3](blocs/bloc3-conteneurisation.md), chaque bloc a sa
   page dédiée ici et **s'appuie sur les précédents** : le bloc 4 réutilise le
   cluster du bloc 3, le bloc 6 réutilisera la CI du bloc 4, etc. Ne saute pas
   d'étape.

## Les choix techniques de ce parcours

Deux adaptations par rapport aux tutoriels classiques, pour tout faire tourner
sur une seule machine, sans dépendre de services externes :

| Outil classique | Ici | Pourquoi |
|---|---|---|
| Docker | **Podman** (rootless) | Libre, sans démon root, API compatible Docker |
| minikube | **kind** | Fiable sur Podman rootless, cluster défini par un fichier YAML versionné |
| GitHub Actions | **Gitea Actions** (auto-hébergé) | Même syntaxe de workflows, tourne en local, registre d'images intégré |
| Docker Hub | **Registre Gitea** | Inclus dans Gitea, aucune limite de pull |
| AWS | **LocalStack** | Simulateur local des APIs AWS, gratuit, aucun compte requis |

!!! tip "Règle d'or"
    Ne copie-colle jamais une commande sans pouvoir expliquer ce qu'elle fait.
    Le critère pour passer au bloc suivant : l'exercice final fonctionne
    **et tu peux l'expliquer sans notes**.
