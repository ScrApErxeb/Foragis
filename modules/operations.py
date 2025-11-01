import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_tables():
    sql_path = Path(__file__).resolve().parents[1] / "data" / "schema_update_v05.sql"
    with connect() as conn, open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("✅ Tables 'operations' et 'paiements_operations' prêtes.")

def enregistrer_operation(type_op, abonne_id, montant):
    with connect() as conn:
        conn.execute(
            "INSERT INTO operations (type_operation, abonne_id, montant) VALUES (?, ?, ?)",
            (type_op, abonne_id, montant)
        )
        conn.commit()
    print("✅ Opération enregistrée.")

def enregistrer_paiement_op(operation_id, montant):
    with connect() as conn:
        conn.execute(
            "INSERT INTO paiements_operations (operation_id, montant) VALUES (?, ?)",
            (operation_id, montant)
        )
        cur = conn.execute("SELECT SUM(montant), (SELECT montant FROM operations WHERE id=?) FROM paiements_operations WHERE operation_id=?", (operation_id, operation_id))
        paye, total = cur.fetchone()
        etat = "soldée" if paye >= total else "partielle"
        conn.execute("UPDATE operations SET etat=? WHERE id=?", (etat, operation_id))
        conn.commit()
    print(f"Paiement enregistré ({paye}/{total}). État = {etat}.")

def lister_operations():
    with connect() as conn:
        cur = conn.execute("SELECT id, type_operation, abonne_id, montant, etat FROM operations ORDER BY date_operation DESC")
        for row in cur.fetchall():
            print(row)

def menu_operations():
    print("=== Gestion des opérations ===")
    print("1. Init tables")
    print("2. Ajouter opération")
    print("3. Ajouter paiement")
    print("4. Lister opérations")
    print("0. Quitter")
    while True:
        c = input("Choix: ").strip()
        if c == "1":
            init_tables()
        elif c == "2":
            type_op = input("Type opération: ")
            abonne_id = int(input("ID abonné: "))
            montant = float(input("Montant: "))
            enregistrer_operation(type_op, abonne_id, montant)
        elif c == "3":
            op_id = int(input("ID opération: "))
            montant = float(input("Montant payé: "))
            enregistrer_paiement_op(op_id, montant)
        elif c == "4":
            lister_operations()
        elif c == "0":
            break
        else:
            print("Option invalide.")

if __name__ == "__main__":
    menu_operations()
