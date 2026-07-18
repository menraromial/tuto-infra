-- Base "opérationnelle" d'exemple : ce qu'une boutique aurait en production.
-- C'est le genre de source qu'on ingère (par batch ou par CDC, voir le cours).

CREATE TABLE clients (
    id         SERIAL PRIMARY KEY,
    code       TEXT NOT NULL UNIQUE,
    nom        TEXT NOT NULL,
    ville      TEXT NOT NULL,
    cree_le    TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO clients (code, nom, ville) VALUES
    ('c001', 'Aline Kamdem',   'Douala'),
    ('c002', 'Brice Nguema',   'Yaoundé'),
    ('c003', 'Clara Mballa',   'Garoua'),
    ('c004', 'David Fotso',    'Bafoussam'),
    ('c005', 'Esther Abena',   'Douala');
