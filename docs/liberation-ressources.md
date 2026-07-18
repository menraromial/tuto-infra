# Libérer les ressources

La plateforme complète (blocs 3 à 11) fait tourner une vingtaine de
conteneurs et consomme plusieurs giga-octets de RAM et de disque. Cette page
explique comment tout arrêter ou tout supprimer proprement, et pourquoi le
faire sans crainte.

## Le principe : détruire est un non-évènement

C'est la thèse du parcours, vérifiée bloc après bloc : **tout est du code**.
Les stacks sont des fichiers compose, le cluster est décrit dans
`cluster.yaml`, les transformations dans dbt, les dashboards sont
provisionnés, les modèles se ré-entraînent d'une commande. La seule chose
qui vive dans l'infrastructure et nulle part ailleurs, ce sont les
**données du lab** (dépôts Gitea locaux, topic Kafka, objets MinIO,
historique Airflow et MLflow), toutes régénérables en rejouant les
exercices. Supprimer l'infrastructure ne détruit aucun savoir : le
dépôt Git contient tout.

## Deux niveaux, un script

```bash
# PAUSE : arrête tous les conteneurs du tuto, conserve toutes les données.
bash scripts/liberer-ressources.sh

# REMISE À ZÉRO : supprime conteneurs, volumes, cluster kind, réseaux
# et images construites par le tuto. Irréversible (mais reconstructible).
bash scripts/liberer-ressources.sh --tout
```

Le script (lis-le, comme toujours) ne touche **que** les ressources du
tutoriel, identifiées par leurs noms exacts : tes autres projets Podman ne
risquent rien.

| | Pause | Remise à zéro (`--tout`) |
|---|---|---|
| Conteneurs | arrêtés | supprimés |
| Volumes (dépôts Gitea, bases, bronze MinIO, historiques...) | conservés | supprimés |
| Cluster kind (ArgoCD, applications déployées) | arrêté | supprimé |
| Réseaux Podman du tuto | conservés | supprimés |
| Images construites (`tuto-airflow`, `tuto-mlflow`, `bloc3-api`) | conservées | supprimées |
| RAM libérée | oui | oui |
| Disque libéré | non | oui (plusieurs Go) |
| Reprise | `podman compose up -d` par stack | rejouer la mise en place des blocs |

Restent volontairement en place dans les deux cas : les fichiers du dépôt
(dont `warehouse.duckdb` et les Parquet de `exercices/bloc6/data/`, ignorés
par Git), les binaires installés (`kind`, `duckdb`, `terraform`), les
venvs Python, et les images publiques téléchargées (PostgreSQL, Redpanda...
un `podman image prune` les nettoie si tu veux aussi ce disque, mais il
touche TOUTES tes images sans tag, pas que celles du tuto).

## Arrêter ou supprimer une seule stack

Chaque stack se gère indépendamment depuis son dossier :

```bash
cd infra/monitoring
podman compose stop        # pause de cette stack seulement
podman compose down -v     # suppression (avec volumes) de cette stack seulement
```

| Stack | Dossier | Blocs |
|---|---|---|
| Forge, CI, registre | `infra/gitea/` | 4, 11 |
| Cluster Kubernetes | `infra/kind/` (`kind delete cluster --name tuto`) | 3, 4, 11 |
| Simulateur AWS | `infra/localstack/` | 5 |
| Kafka + PostgreSQL | `infra/ingestion/` | 6 |
| MinIO | `infra/lake/` | 7 |
| Airflow | `infra/airflow/` | 9, 11 |
| Prometheus + Grafana | `infra/monitoring/` | 10, 11 |
| MLflow | `infra/mlflow/` | 11 |

C'est aussi le bon réflexe **pendant** le parcours : le bloc 11 a besoin de
presque tout, mais le bloc 6 n'a pas besoin de Grafana. Sur une machine à
16 Go, ne fais tourner que ce que le bloc courant utilise (le dépannage du
bloc 11 raconte ce qui arrive sinon : le noyau se met à tuer des processus).

## Tout reconstruire

L'ordre de reconstruction est simplement l'ordre du parcours : cluster et
réglages système (bloc 3), Gitea et ArgoCD (bloc 4), puis chaque stack au
fil des blocs. Chaque page contient sa mise en place, et le bloc 11 son
pas-à-pas complet. Si la reconstruction te semble longue : tu tiens une
excellente idée d'exercice Ansible ou de script, exactement le genre
d'automatisation qu'un ingénieur plateforme écrirait.
