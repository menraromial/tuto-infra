-- Table de FAITS : une ligne par commande (le grain), des clés vers les
-- dimensions, et les mesures numériques qu'on agrège.

with commandes as (

    select * from {{ ref('stg_commandes') }}

)

select
    event_id,
    client_id as client_code,      -- clé vers dim_clients
    produit as produit_code,       -- clé vers dim_produits
    cast(horodate_a as date) as jour,
    quantite,
    prix_unitaire,
    quantite * prix_unitaire as montant

from commandes
