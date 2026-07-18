-- Dimension clients : le référentiel (seed), prêt à être enrichi.
-- Dans une vraie plateforme, cette table viendrait de la base opérationnelle
-- (celle du bloc 6) via une ingestion batch ou du CDC.

select
    code as client_code,
    nom,
    ville

from {{ ref('clients') }}
