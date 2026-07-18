-- Test de COHÉRENCE TEMPORELLE (bloc 8) : aucune commande ne peut venir
-- du futur. Ce genre d'anomalie révèle une horloge mal réglée ou un bug
-- de parsing de date en amont.

select event_id, jour
from {{ ref('fct_commandes') }}
where jour > current_date
