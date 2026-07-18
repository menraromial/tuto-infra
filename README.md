# Socle infrastructure & data engineering

Parcours pratique en 10 blocs : terminal, Git, conteneurs (Podman), Kubernetes
(kind), CI/CD GitOps (Gitea Actions + ArgoCD), IaC, ingestion, lake/warehouse,
orchestration, monitoring. **Entièrement en local, sans carte bancaire.**

📖 **Le tutoriel complet : [menraromial.github.io/tuto-infra](https://menraromial.github.io/tuto-infra/)**

## Structure du dépôt

```
docs/        # le site du tutoriel (MkDocs Material)
infra/       # infrastructure locale : cluster kind, stack Gitea, ArgoCD, Podman
exercices/   # solutions des exercices finaux de chaque bloc
scripts/     # réglages hôte (une fois par machine)
```

## Démarrage rapide (blocs 3-4)

```bash
sudo bash scripts/setup-hote.sh          # /etc/hosts + limites inotify
bash infra/kind/create-cluster.sh        # cluster Kubernetes local
cd infra/gitea && podman compose up -d gitea   # forge + CI + registre (voir docs bloc 4)
```

## Prévisualiser le site en local

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-docs.txt
.venv/bin/mkdocs serve   # → http://127.0.0.1:8000
```
