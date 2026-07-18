-- Couche ARGENT : le bronze nettoyé.
-- 1. Lecture directe des Parquet bruts dans MinIO (schéma à la lecture).
-- 2. Déduplication par event_id : le bloc 6 garantit "au moins une fois",
--    c'est donc ICI que l'idempotence de la plateforme se joue.
-- 3. Typage propre (l'horodatage texte devient un vrai timestamp).

with brut as (

    -- union_by_name : les fichiers anciens et récents n'ont pas forcément
    -- les mêmes colonnes (le champ signalement_fraude est apparu au
    -- bloc 11) ; DuckDB aligne les schémas par nom de colonne.
    select *
    from read_parquet('s3://lake/bronze/commandes/*.parquet', union_by_name = true)

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
    cast(horodatage as timestamptz) as horodate_a,
    -- Les commandes d'avant le bloc 11 n'ont pas de signalement : false.
    coalesce(signalement_fraude, false) as signalement_fraude

from dedoublonne
where rang = 1
