import sqlite3
from core.audit_manager import audit_after_action
from pathlib import Path
from core.validator import (
    validate_id_exists,
    validate_positive_amount,
    validate_schema_columns
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_tables():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_operation TEXT NOT NULL,
            abonne_id INTEGER NOT NULL,
            montant REAL NOT NULL,
            date_operation TEXT DEFAULT CURRENT_TIMESTAMP,
            etat TEXT DEFAULT 'non payé',
            saisi_par TEXT DEFAULT 'system'
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS paiements_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_id INTEGER NOT NULL,
            montant REAL NOT NULL,
            mode_paiement TEXT DEFAULT 'cash',
            date_paiement TEXT DEFAULT CURRENT_TIMESTAMP,
            saisi_par TEXT DEFAULT 'system'
        )
        """)
        conn.commit()
    print("✅ Tables 'operations' et 'paiements_operations' prêtes.")

def ajouter_operation():
    try:
        type_op = input("Type opération: ")
        abonne_id = int(input("ID abonné: "))
        montant = float(input("Montant: "))
    except ValueError:
        print("❌ Entrée invalide.")
        audit_after_action("❌ Entrée invalide.")
        return

    if not validate_positive_amount(montant):
        return

    with connect() as conn:
        conn.execute(
            "INSERT INTO operations (type_operation, abonne_id, montant) VALUES (?, ?, ?)",
            (type_op, abonne_id, montant)
        )
        conn.commit()
    print("✅ Opération enregistrée.")
    audit_after_action("✅ Opération enregistrée.")

def enregistrer_paiement_op():
    try:
        operation_id = int(input("ID opération: "))
        montant = float(input("Montant payé: "))
    except ValueError:
        print("❌ Entrée invalide.")
        audit_after_action("❌ Entrée invalide.")

        return

    if not validate_id_exists("operations", operation_id):
        return
    if not validate_positive_amount(montant):
        return

    with connect() as conn:
        cur = conn.execute("SELECT montant FROM operations WHERE id=?", (operation_id,))
        row = cur.fetchone()
        if not row:
            print("❌ Opération introuvable.")
            audit_after_action(f"❌ Opération introuvable. ID: {operation_id}")
            return

        total = row[0]
        cur = conn.execute("SELECT SUM(montant) FROM paiements_operations WHERE operation_id=?", (operation_id,))
        deja_paye = cur.fetchone()[0] or 0.0
        reste = total - deja_paye

        if montant > reste:
            print(f"⚠ Paiement refusé : montant ({montant}) dépasse le reste dû ({reste}).")
            audit_after_action(f"⚠ Paiement refusé : montant ({montant}) dépasse le reste dû ({reste}). ID opération: {operation_id}")
            return

        conn.execute(
            "INSERT INTO paiements_operations (operation_id, montant) VALUES (?, ?)",
            (operation_id, montant)
        )
        nouveau_total = deja_paye + montant
        etat = "soldée" if nouveau_total >= total else "partielle"
        conn.execute("UPDATE operations SET etat=? WHERE id=?", (etat, operation_id))
        conn.commit()
        print(f"✅ Paiement enregistré ({nouveau_total}/{total}). État = {etat}.")
        audit_after_action(f"✅ Paiement enregistré ({nouveau_total}/{total}). État = {etat}. ID opération: {operation_id}")

def lister_operations():
    with connect() as conn:
        for row in conn.execute("""
        SELECT o.id, o.type_operation, o.montant,
               IFNULL(SUM(p.montant), 0) AS total_paye,
               o.etat
        FROM operations o
        LEFT JOIN paiements_operations p ON o.id = p.operation_id
        GROUP BY o.id
        ORDER BY o.id DESC
        """):
            print(f"[{row[0]}] {row[1]} : {row[3]}/{row[2]} ({row[4]})")
            
def menu():
    print("=== Gestion des opérations ===")
    print("1. Init tables")
    print("2. Ajouter opération")
    print("3. Ajouter paiement")
    print("4. Lister opérations")
    print("0. Quitter")
    choix = input("Choix: ")
    if choix == "1":
        init_tables()
    elif choix == "2":
        ajouter_operation()
    elif choix == "3":
        enregistrer_paiement_op()
    elif choix == "4":
        lister_operations()
    elif choix == "0":
        return

if __name__ == "__main__":
    while True:
        menu()
