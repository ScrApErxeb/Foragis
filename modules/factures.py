import sqlite3
from core.audit_manager import audit_after_action
from pathlib import Path
from core.validator import (
    validate_id_exists,
    validate_positive_amount,
    validate_schema_columns
)

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
    if not validate_schema_columns("consommations", ["id", "volume_m3"]):
        return
    if not validate_id_exists("consommations", consommation_id):
        return

    with connect() as conn:
        cur = conn.execute("SELECT volume_m3 FROM consommations WHERE id=?", (consommation_id,))
        row = cur.fetchone()
        if not row:
            print("❌ Consommation introuvable.")
            audit_after_action(f"Échec génération facture : consommation {consommation_id} introuvable")
            return

        volume = row[0]
        montant = volume * TARIF_UNITAIRE
        if not validate_positive_amount(montant):
            return

        conn.execute(
            "INSERT INTO factures (operation_id, montant_total) VALUES (?, ?)",
            (consommation_id, montant)
        )
        conn.commit()
        print(f"✅ Facture créée pour consommation {consommation_id} → {montant} F CFA")
        audit_after_action(f"Facture générée pour consommation {consommation_id} → {montant} F CFA")

def lister_factures():
    with connect() as conn:
        cur = conn.execute(
            "SELECT f.id, f.operation_id, f.montant_total, f.statut, f.date_creation "
            "FROM factures f ORDER BY f.date_creation DESC"
        )
        for r in cur.fetchall():
            print(r)

def marquer_paye(facture_id):
    if not validate_id_exists("factures", facture_id):
        return
    with connect() as conn:
        conn.execute("UPDATE factures SET paye=1 WHERE id=?", (facture_id,))
        conn.commit()
    print(f"✅ Facture {facture_id} marquée comme payée.")
    audit_after_action(f"Facture {facture_id} marquée comme payée.")
    
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
