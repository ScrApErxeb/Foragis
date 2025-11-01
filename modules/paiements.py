import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_table():
    sql_path = Path(__file__).resolve().parents[1] / "data" / "schema_update_v04.sql"
    with connect() as conn, open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("✅ Table 'paiements' prête.")

def enregistrer_paiement(facture_id, montant):
    with connect() as conn:
        cur = conn.execute("SELECT montant, paye FROM factures WHERE id=?", (facture_id,))
        row = cur.fetchone()
        if not row:
            print("❌ Facture introuvable.")
            return
        total, paye = row
        if paye == 1:
            print("⚠ Facture déjà soldée.")
            return
        cur = conn.execute("SELECT SUM(montant) FROM paiements WHERE facture_id=?", (facture_id,))
        deja_paye = cur.fetchone()[0] or 0
        nouveau_total = deja_paye + montant
        conn.execute(
            "INSERT INTO paiements (facture_id, montant) VALUES (?, ?)",
            (facture_id, montant)
        )
        if nouveau_total >= total:
            conn.execute("UPDATE factures SET paye=1 WHERE id=?", (facture_id,))
            print("✅ Paiement total atteint. Facture soldée.")
        else:
            print(f"Paiement partiel enregistré ({nouveau_total}/{total}).")
        conn.commit()

def lister_paiements(facture_id=None):
    with connect() as conn:
        if facture_id:
            cur = conn.execute(
                "SELECT id, montant, date_paiement FROM paiements WHERE facture_id=? ORDER BY date_paiement",
                (facture_id,)
            )
        else:
            cur = conn.execute(
                "SELECT facture_id, SUM(montant) as total FROM paiements GROUP BY facture_id"
            )
        rows = cur.fetchall()
    for r in rows:
        print(r)

def menu_paiements():
    print("=== Gestion des Paiements ===")
    print("1. Init table")
    print("2. Enregistrer paiement")
    print("3. Lister paiements")
    print("0. Quitter")
    while True:
        choix = input("Choix: ").strip()
        if choix == "1":
            init_table()
        elif choix == "2":
            facture_id = int(input("ID facture: "))
            montant = float(input("Montant payé: "))
            enregistrer_paiement(facture_id, montant)
        elif choix == "3":
            fid = input("Facture ID (laisser vide pour tout): ").strip()
            lister_paiements(int(fid) if fid else None)
        elif choix == "0":
            break
        else:
            print("Option invalide.")

if __name__ == "__main__":
    menu_paiements()
