import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_table():
    sql_path = Path(__file__).resolve().parents[1] / "data" / "schema_update_v02.sql"
    with connect() as conn, open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("✅ Table 'consommations' prête.")

def ajouter_releve(compteur_id, mois, volume_m3):
    try: 
        with connect() as conn:
            conn.execute(
                "INSERT INTO consommations (compteur_id, mois, volume_m3) VALUES (?, ?, ?)",
                (compteur_id, mois, volume_m3),
            )
            conn.commit()
        print(f"Relevé ajouté : compteur={compteur_id}, mois={mois}, volume={volume_m3} m³")
    except sqlite3.IntegrityError:
        print("⚠ Relevé déjà existant pour ce compteur et ce mois.")

def lister_releves(compteur_id=None):
    with connect() as conn:
        if compteur_id:
            cur = conn.execute(
                "SELECT id, compteur_id, mois, volume_m3, valide FROM consommations WHERE compteur_id=? ORDER BY mois DESC",
                (compteur_id,),
            )
        else:
            cur = conn.execute(
                "SELECT id, compteur_id, mois, volume_m3, valide FROM consommations ORDER BY compteur_id, mois DESC"
            )
        rows = cur.fetchall()
    for r in rows:
        print(r)

def menu_consommations():
    print("=== Gestion des Consommations ===")
    print("1. Init table")
    print("2. Ajouter relevé")
    print("3. Lister relevés")
    print("0. Quitter")
    while True:
        choix = input("Choix: ").strip()
        if choix == "1":
            init_table()
        elif choix == "2":
            compteur_id = int(input("ID compteur: "))
            mois = input("Mois (ex: 2025-11): ").strip()
            volume = float(input("Volume m³: "))
            ajouter_releve(compteur_id, mois, volume)
        elif choix == "3":
            filtre = input("Filtrer par ID compteur (laisser vide pour tous): ").strip()
            lister_releves(int(filtre) if filtre else None)
        elif choix == "0":
            break
        else:
            print("Option invalide.")

if __name__ == "__main__":
    menu_consommations()
