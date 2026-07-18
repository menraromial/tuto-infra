-- Couche ARGENT : le bronze nettoyé.
-- 1. Lecture directe des Parquet bruts dans MinIO (schéma à la lecture).
-- 2. Déduplication par event_id : le bloc 6 garantit "au moins une fois",
--    c'est donc ICI que l'idempotence de la plateforme se joue.
-- 3. Typage propre (l'horodatage texte devient un vrai timestamp).

with brut as (

    select *
    from read_parquet('s3://lake/bronze/commandes/*.parquet')

),

dedoublonne as (

    select
        *,
        row_number() over (
            partition by event_id
            order by horodatage
        ) as rang

    from brut

)

select
    event_id,
    client_id,
    produit,
    quantite,
    prix_unitaire,
    cast(horodatage as timestamptz) as horodate_a

from dedoublonne
where rang = 1
