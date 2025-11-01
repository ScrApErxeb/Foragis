-- === Schéma Foragis V0.4B ===
-- Création ou mise à jour des tables principales

CREATE TABLE IF NOT EXISTS factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER,
    montant_total REAL NOT NULL,
    statut TEXT DEFAULT 'non payé',
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_id INTEGER NOT NULL,
    montant REAL NOT NULL,
    mode_paiement TEXT DEFAULT 'cash',
    date_paiement TEXT DEFAULT CURRENT_TIMESTAMP,
    saisi_par TEXT DEFAULT 'system',
    FOREIGN KEY (facture_id) REFERENCES factures(id)
);
