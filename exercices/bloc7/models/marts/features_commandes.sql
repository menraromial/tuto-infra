-- Table de FEATURES du bloc 11 : une ligne par commande, les variables
-- explicatives calculées en SQL, et le label (signalement a posteriori).
-- Le service de scoring recalcule les mêmes features à la volée : garder
-- cette logique EN SQL, simple et lisible, limite le risque de divergence
-- entre l'entraînement et la production (le "training/serving skew").

with commandes as (

    select * from {{ ref('stg_commandes') }}

),

prix_reference as (

    -- Le prix "normal" de chaque produit : la médiane observée.
    select
        produit,
        median(prix_unitaire) as prix_median

    from commandes
    group by produit

)

select
    c.event_id,
    c.horodate_a,

    -- Les features :
    c.quantite,
    c.quantite * c.prix_unitaire as montant,
    c.prix_unitaire / p.prix_median as ratio_prix,
    count(*) over (
        partition by c.client_id, cast(c.horodate_a as date)
    ) as commandes_client_jour,

    -- Le label (jamais fourni au service en production) :
    c.signalement_fraude

from commandes c
join prix_reference p using (produit)
