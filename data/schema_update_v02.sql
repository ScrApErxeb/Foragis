CREATE TABLE IF NOT EXISTS consommations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compteur_id INTEGER NOT NULL,
    mois TEXT NOT NULL,
    volume_m3 REAL NOT NULL,
    valide INTEGER DEFAULT 1,
    UNIQUE(compteur_id, mois),
    FOREIGN KEY (compteur_id) REFERENCES compteurs(id)
);
