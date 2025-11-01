CREATE TABLE IF NOT EXISTS abonnes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT,
    cnib TEXT UNIQUE,
    telephone TEXT
);

CREATE TABLE IF NOT EXISTS compteurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_compteur TEXT UNIQUE NOT NULL,
    abonne_id INTEGER,
    actif INTEGER DEFAULT 1,
    FOREIGN KEY (abonne_id) REFERENCES abonnes(id)
);
