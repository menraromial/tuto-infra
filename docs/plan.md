# Socle infrastructure et data engineering

Parcours en 10 blocs : terminal, Git, conteneurisation, CI/CD, infrastructure as code, ingestion de donnees, lake et warehouse, pipelines, orchestration, monitoring. Tout se pratique en local (docker compose, minikube) ou sur des labs navigateur gratuits, sans carte bancaire.

Colonne vertebrale recommandee : le [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) de DataTalks.Club, gratuit et open source, qui couvre Terraform, l'orchestration, le warehouse, le batch et le streaming. Toutes ses videos sont sur la [chaine YouTube DataTalksClub](https://www.youtube.com/@DataTalksClub), telechargeables en basse resolution pour travailler hors ligne.

Ordre conseille : les blocs 1 a 5 sont les fondations, a faire dans l'ordre. Les blocs 6 a 9 forment le coeur data. Le bloc 10 se pose par-dessus tout le reste.

---

## Bloc 1 : Le terminal Linux et Bash

Mise en place : sous Windows, installer WSL (une commande : wsl --install). Sous Linux ou Mac, rien a installer.

- Navigation : cd, ls, pwd, find, arborescence de fichiers
- Manipulation : cp, mv, rm, mkdir, cat, less, head, tail
- Le pouvoir des pipes : grep, sort, uniq, wc, redirection > et >>
- Variables, boucles et conditions dans un script .sh
- Permissions (chmod), processus (ps, kill), ssh

Ressources :
- [MIT Missing Semester](https://missing.csail.mit.edu/) (notes en texte, legeres a charger)
- Cours video gratuits : les videos du Missing Semester sur la meme page ; sur YouTube, "Linux for Beginners" et "Bash Scripting Tutorial" de la chaine freeCodeCamp

Exercice final : ecrire un script qui parcourt un dossier, compte les fichiers par extension et affiche un resume.

---

## Bloc 2 : Git et GitHub

Mise en place : sudo apt install git, puis creer un compte GitHub gratuit.

- init, add, commit, status, log : le cycle de base
- Branches : creer, fusionner, resoudre un conflit a la main
- Depots distants : clone, push, pull
- Pull requests : en ouvrir une, la relire, la fusionner
- .gitignore et bons messages de commit

Ressources :
- [Learn Git Branching](https://learngitbranching.js.org/?locale=fr_FR) (interactif, en francais)
- [Pro Git](https://git-scm.com/book/fr/v2) (livre gratuit en francais, telechargeable)
- Cours video gratuits : sur YouTube, "Git and GitHub for Beginners" de freeCodeCamp ; en francais, les tutoriels Git de la chaine Grafikart

Exercice final : mettre le script du bloc 1 sur GitHub, creer une branche, modifier le script, ouvrir et fusionner une pull request.

---

## Bloc 3 : Conteneurisation, Docker puis Kubernetes

Mise en place : Docker Engine ou Docker Desktop, puis minikube ou kind.

### Docker
- Images vs conteneurs, cycle de vie, registres
- Dockerfile : layers, cache, multi-stage builds
- Volumes, reseaux, variables d'environnement
- docker compose : stack multi-services (ce sera l'outil de tous les blocs suivants)

### Kubernetes
- Architecture : control plane, nodes, kubelet
- Pods, Deployments, ReplicaSets, Services (ClusterIP, NodePort)
- ConfigMaps, Secrets, Namespaces
- Requests et limits, probes (liveness, readiness)
- Helm : installer et parametrer un chart existant

Ressources :
- [Docker Curriculum](https://docker-curriculum.com/) (texte)
- [Tutoriels officiels Kubernetes](https://kubernetes.io/fr/docs/tutorials/) (en francais)
- [Killercoda](https://killercoda.com/) (labs K8s dans le navigateur, gratuits)
- Cours video gratuits : sur YouTube, "Docker Tutorial for Beginners" (environ 3 h) et "Kubernetes Tutorial for Beginners" (environ 4 h) de la chaine TechWorld with Nana ; cours gratuits [KodeKloud](https://kodekloud.com/free-courses) avec labs integres

Exercice final : deployer sur minikube une petite stack de deux services qui communiquent, avec ConfigMap et probes.

---

## Bloc 4 : CI/CD

Mise en place : un depot GitHub gratuit, rien d'autre.

- Anatomie d'un pipeline : trigger, jobs, steps, artefacts
- GitHub Actions : workflow de test, build d'image Docker, push vers un registre
- Secrets et environnements dans les pipelines
- Strategies de deploiement : rolling, blue-green, canary (concepts)
- GitOps : le principe (le depot Git comme source de verite), decouverte d'ArgoCD sur minikube

Ressources :
- [Documentation GitHub Actions](https://docs.github.com/actions)
- [ArgoCD, getting started](https://argo-cd.readthedocs.io/en/stable/getting_started/) (s'installe sur minikube)
- Cours video gratuits : sur YouTube, "GitHub Actions Tutorial" et "ArgoCD Tutorial for Beginners" de TechWorld with Nana ; "DevOps CI/CD Explained" de freeCodeCamp

Exercice final : pipeline qui construit une image a chaque push, la pousse sur Docker Hub, et un ArgoCD local qui deploie automatiquement sur minikube.

---

## Bloc 5 : Infrastructure as code, Terraform et Ansible

Mise en place : binaires terraform et ansible, plus LocalStack (simulateur AWS gratuit en conteneur) pour pratiquer sans compte cloud.

### Terraform
- Providers, resources, state : le modele mental
- Variables, outputs, modules
- plan et apply : lire un plan avant de l'appliquer
- Pratiquer contre LocalStack (S3, bases de donnees simulees) ou le provider Docker

### Ansible
- Inventaires, playbooks, taches, idempotence
- Roles et templates (Jinja2)
- Cible d'entrainement : des conteneurs Docker ou une VM locale comme hotes

Ressources :
- [Terraform tutorials, HashiCorp](https://developer.hashicorp.com/terraform/tutorials) (gratuit)
- [LocalStack](https://docs.localstack.cloud/) (gratuit en version communautaire)
- [Documentation Ansible](https://docs.ansible.com/ansible/latest/getting_started/index.html)
- Cours video gratuits : sur YouTube, "Terraform Course" de freeCodeCamp (environ 2 h) ; la serie "Ansible 101" de Jeff Geerling (une douzaine d'episodes, par l'auteur du livre de reference) ; module Terraform du Data Engineering Zoomcamp

Exercice final : un Terraform qui cree un bucket S3 sur LocalStack, et un playbook Ansible qui configure deux conteneurs comme des serveurs.

---

## Bloc 6 : Architecture d'ingestion de donnees

Mise en place : docker compose avec PostgreSQL et Redpanda (Kafka leger, une seule image).

- Batch vs streaming vs micro-batch : quand choisir quoi
- Sources : bases operationnelles, APIs, fichiers, evenements
- Formats de donnees : CSV, JSON, Parquet, Avro (et pourquoi Parquet gagne)
- Kafka : topics, partitions, producers, consumers, offsets
- Change Data Capture : le concept, apercu de Debezium
- Idempotence et gestion des doublons a l'ingestion

Ressources :
- [Data Engineering Zoomcamp, module streaming](https://github.com/DataTalksClub/data-engineering-zoomcamp)
- [Redpanda quickstart](https://docs.redpanda.com/current/get-started/quick-start/) (Kafka compatible, leger, une commande)
- Cours video gratuits : [Kafka 101 sur Confluent Developer](https://developer.confluent.io/courses/) (serie de videos courtes, gratuites) ; videos du module streaming du Zoomcamp sur la chaine DataTalksClub

Exercice final : un producer qui envoie des evenements JSON dans un topic, un consumer qui les ecrit en Parquet.

---

## Bloc 7 : Data lake et data warehouse

Mise en place : docker compose avec MinIO (stockage objet compatible S3) et DuckDB ou PostgreSQL.

- Lake vs warehouse vs lakehouse : les differences reelles
- Architecture medaillon : bronze, argent, or
- Modelisation warehouse : schema en etoile, faits et dimensions, slowly changing dimensions
- Partitionnement et formats colonnes (Parquet) pour la performance
- Transformations SQL avec dbt : models, tests, documentation
- Apercu des formats de tables : Delta Lake, Iceberg (concepts)

Ressources :
- [MinIO quickstart](https://min.io/docs/minio/container/index.html) (un conteneur)
- [DuckDB](https://duckdb.org/docs/) (un binaire, aucune installation serveur)
- [dbt, tutoriel officiel](https://docs.getdbt.com/guides) (gratuit avec dbt-core)
- [Data Engineering Zoomcamp, modules warehouse et analytics](https://github.com/DataTalksClub/data-engineering-zoomcamp)
- Cours video gratuits : [dbt Learn](https://learn.getdbt.com/) (cours officiels gratuits en video, dont dbt Fundamentals) ; videos des modules warehouse et analytics engineering du Zoomcamp sur YouTube

Exercice final : les Parquet du bloc 6 poses dans MinIO (bronze), transformes avec dbt vers un schema en etoile dans DuckDB ou PostgreSQL (or).

---

## Bloc 8 : Data pipelines, la vue d'ensemble

Ce bloc relie les blocs 6 et 7 en une architecture complete.

- Anatomie d'un pipeline : extraction, validation, transformation, chargement, publication
- ELT vs ETL : pourquoi le moderne est plutot ELT
- Qualite de donnees : tests de schema, de fraicheur, de volume
- Backfills et re-runs : concevoir pour la reprise sur erreur
- Lineage : savoir d'ou vient chaque table

Ressources :
- [Data Engineering Zoomcamp, fil complet du projet](https://github.com/DataTalksClub/data-engineering-zoomcamp)
- Cours video gratuits : la playlist complete du Zoomcamp sur la chaine DataTalksClub suit exactement ce fil, du brut au dashboard

Exercice final : dessiner (sur papier ou diagramme) l'architecture complete de ton pipeline des blocs 6 et 7, avec les points de defaillance et la strategie de reprise.

---

## Bloc 9 : Orchestration et deploiement, Airflow et Kubeflow

Mise en place : Airflow via docker compose (officiel). Kubeflow Pipelines sur minikube en seconde etape (plus lourd, prevoir 8 Go de RAM).

### Airflow
- DAGs, tasks, operators, dependances
- Scheduling, catchup, backfill
- Idempotence des taches, retries, alerting
- Connections et variables

### Kubeflow (apercu oriente ML)
- Kubeflow Pipelines : composants, artefacts, experiences
- Quand Kubeflow plutot qu'Airflow (workloads ML sur Kubernetes)

Ressources :
- [Airflow, docker compose officiel](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
- [Kubeflow Pipelines, installation locale](https://www.kubeflow.org/docs/components/pipelines/)
- Cours video gratuits : [Astronomer Academy](https://academy.astronomer.io/) (cours Airflow officiels gratuits, dont Airflow 101) ; module orchestration du Zoomcamp sur YouTube ; sur YouTube, "Airflow Tutorial for Beginners" de coder2j

Exercice final : orchestrer le pipeline des blocs 6 et 7 dans un DAG Airflow avec retries et planification quotidienne.

---

## Bloc 10 : Monitoring et observabilite, Prometheus et Grafana

Mise en place : docker compose avec Prometheus, Grafana et node-exporter.

- Les trois piliers : metriques, logs, traces
- Prometheus : scraping, exporters, PromQL de base
- Grafana : datasources, dashboards, variables
- Alerting : regles Prometheus, notions de SLI et SLO
- Monitorer les blocs precedents : Airflow, Kafka et Kubernetes exposent tous des metriques Prometheus

Ressources :
- [Prometheus, getting started](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [Grafana, documentation](https://grafana.com/docs/grafana/latest/)
- Cours video gratuits : sur YouTube, "Prometheus Monitoring Tutorial" de TechWorld with Nana ; "Grafana for Beginners", la serie officielle de la chaine Grafana

Exercice final : un dashboard Grafana qui montre la sante du pipeline complet (taches Airflow, lag Kafka, ressources du cluster) avec une alerte si le DAG echoue.

---

## Le fil conducteur

A la fin du parcours, tu as construit une mini plateforme data complete qui tourne sur ta machine : des evenements ingeres via Kafka, stockes en Parquet dans un lake MinIO, transformes avec dbt vers un warehouse en etoile, orchestres par Airflow deploye sur Kubernetes, provisionnes par Terraform et Ansible, livres par un pipeline CI/CD GitOps, et surveilles par Prometheus et Grafana. Le tout versionne dans Git et manipule au terminal. C'est exactement l'architecture qu'on retrouve en entreprise, en version reduite.

Rythme suggere : 1 semaine pour chacun des blocs 1 et 2, puis 2 a 3 semaines par bloc. Le critere pour avancer reste le meme : l'exercice final fonctionne et tu peux l'expliquer sans notes.