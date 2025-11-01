import sqlite3
from core.audit_manager import audit_after_action
from pathlib import Path
from core.validator import (
    validate_id_exists,
    validate_positive_amount,
    validate_schema_columns
)

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_table():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS paiements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facture_id INTEGER NOT NULL,
            montant REAL NOT NULL,
            mode_paiement TEXT DEFAULT 'cash',
            date_paiement TEXT DEFAULT CURRENT_TIMESTAMP,
            saisi_par TEXT DEFAULT 'system'
        )
        """)
        conn.commit()
    print("✅ Table 'paiements' prête.")

def enregistrer_paiement():
    if not validate_schema_columns("paiements", ["id", "facture_id", "montant"]):
        return
    if not validate_schema_columns("factures", ["id", "montant_total"]):
        return

    try:
        facture_id = int(input("ID facture: "))
        montant = float(input("Montant payé: "))
    except ValueError:
        print("❌ Entrée invalide.")
        audit_after_action("❌ Entrée invalide.")
        return

    if not validate_id_exists("factures", facture_id):
        return
    if not validate_positive_amount(montant):
        return

    with connect() as conn:
        cur = conn.execute("SELECT montant_total FROM factures WHERE id=?", (facture_id,))
        row = cur.fetchone()
        if not row:
            print("❌ Facture introuvable.")
            audit_after_action(f"❌ Facture introuvable. ID: {facture_id}")
            return

        total = row[0]
        cur = conn.execute("SELECT SUM(montant) FROM paiements WHERE facture_id=?", (facture_id,))
        deja_paye = cur.fetchone()[0] or 0.0
        reste = total - deja_paye

        if montant > reste:
            print(f"⚠ Paiement refusé : montant ({montant}) dépasse le reste dû ({reste}).")
            audit_after_action(f"⚠ Paiement refusé : montant ({montant}) dépasse le reste dû ({reste}). ID facture: {facture_id}")
            return

        conn.execute(
            "INSERT INTO paiements (facture_id, montant) VALUES (?, ?)",
            (facture_id, montant)
        )

        nouveau_total = deja_paye + montant
        statut = "soldée" if nouveau_total >= total else "partielle"
        conn.execute("UPDATE factures SET statut=? WHERE id=?", (statut, facture_id))
        conn.commit()

        print(f"✅ Paiement enregistré ({nouveau_total}/{total}). Statut = {statut}.")
        audit_after_action(f"✅ Paiement enregistré pour facture {facture_id} ({nouveau_total}/{total}). Statut = {statut}.")

def lister_paiements():
    with connect() as conn:
        for row in conn.execute("""
        SELECT p.id, p.facture_id, p.montant, p.date_paiement, f.montant_total
        FROM paiements p
        JOIN factures f ON p.facture_id = f.id
        ORDER BY p.date_paiement DESC
        """):
            print(f"[{row[0]}] facture {row[1]} → {row[2]} F / {row[4]} F (le {row[3]})")

def menu_paiements():
    print("=== Gestion des paiements ===")
    print("1. Init table")
    print("2. Enregistrer paiement")
    print("3. Lister paiements")
    print("0. Quitter")
    while True:
        choix = input("Choix: ").strip()
        if choix == "1":
            init_table()
        elif choix == "2":
            enregistrer_paiement()
        elif choix == "3":
            lister_paiements()
        elif choix == "0":
            break
        else:
            print("Option invalide.")

if __name__ == "__main__":
    menu_paiements()
