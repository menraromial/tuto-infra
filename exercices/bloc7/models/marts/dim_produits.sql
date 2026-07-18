-- Dimension produits, dérivée des évènements (pas de référentiel produit
-- dans notre lab). Le prix "catalogue" est le dernier prix observé.

with commandes as (

    select * from {{ ref('stg_commandes') }}

)

select
    produit as produit_code,
    max(prix_unitaire) as prix_catalogue,
    count(*) as nb_commandes_observees

from commandes
group by produit
