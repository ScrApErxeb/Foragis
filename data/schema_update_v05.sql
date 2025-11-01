CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_operation TEXT NOT NULL,
    abonne_id INTEGER NOT NULL,
    montant REAL NOT NULL,
    date_operation TEXT DEFAULT CURRENT_TIMESTAMP,
    etat TEXT DEFAULT 'en attente',
    FOREIGN KEY (abonne_id) REFERENCES abonnes(id)
);

CREATE TABLE IF NOT EXISTS paiements_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    montant REAL NOT NULL,
    mode_paiement TEXT DEFAULT 'cash',
    date_paiement TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);
