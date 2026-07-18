-- Test de VOLUME (bloc 8) : un test "singulier" dbt échoue s'il renvoie
-- au moins une ligne. Ici : alerte si la table de faits contient moins de
-- 100 commandes, signe d'une ingestion partielle ou cassée.

select count(*) as nb_lignes
from {{ ref('fct_commandes') }}
having count(*) < 100
