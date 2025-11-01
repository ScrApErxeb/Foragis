CREATE TABLE IF NOT EXISTS factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consommation_id INTEGER NOT NULL,
    montant REAL NOT NULL,
    paye INTEGER DEFAULT 0,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consommation_id) REFERENCES consommations(id)
);
