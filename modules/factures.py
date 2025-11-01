import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"
TARIF_UNITAIRE = 500  # par m³

def connect():
    return sqlite3.connect(DB_PATH)

def init_table():
    sql_path = Path(__file__).resolve().parents[1] / "data" / "schema_update_v03.sql"
    with connect() as conn, open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("✅ Table 'factures' prête.")

def generer_facture(consommation_id):
    with connect() as conn:
        cur = conn.execute("SELECT volume_m3 FROM consommations WHERE id=?", (consommation_id,))
        row = cur.fetchone()
        if not row:
            print("❌ Consommation introuvable.")
            return
        volume = row[0]
        montant = volume * TARIF_UNITAIRE
        conn.execute(
            "INSERT INTO factures (consommation_id, montant) VALUES (?, ?)",
            (consommation_id, montant)
        )
        conn.commit()
        print(f"Facture créée pour consommation {consommation_id} → {montant} F CFA")

def lister_factures():
    with connect() as conn:
        cur = conn.execute(
            "SELECT f.id, f.consommation_id, f.montant, f.paye, f.date_creation "
            "FROM factures f ORDER BY f.date_creation DESC"
        )
        rows = cur.fetchall()
    for r in rows:
        print(r)

def marquer_paye(facture_id):
    with connect() as conn:
        conn.execute("UPDATE factures SET paye=1 WHERE id=?", (facture_id,))
        conn.commit()
    print(f"✅ Facture {facture_id} marquée comme payée.")

def menu_factures():
    print("=== Gestion des Factures ===")
    print("1. Init table")
    print("2. Générer facture")
    print("3. Lister factures")
    print("4. Marquer facture payée")
    print("0. Quitter")
    while True:
        choix = input("Choix: ").strip()
        if choix == "1":
            init_table()
        elif choix == "2":
            consommation_id = int(input("ID consommation: "))
            generer_facture(consommation_id)
        elif choix == "3":
            lister_factures()
        elif choix == "4":
            facture_id = int(input("ID facture: "))
            marquer_paye(facture_id)
        elif choix == "0":
            break
        else:
            print("Option invalide.")

if __name__ == "__main__":
    menu_factures()
