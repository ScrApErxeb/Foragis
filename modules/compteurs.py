import sqlite3
from pathlib import Path
from core.audit_manager import audit_after_action


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_tables():
    sql_path = Path(__file__).resolve().parents[1] / "data" / "schema_update_v01.sql"
    with connect() as conn, open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("✅ Tables 'abonnes' et 'compteurs' disponibles.")

def ajouter_abonne(nom, prenom, cnib, telephone):
    with connect() as conn:
        conn.execute(
            "INSERT INTO abonnes (nom, prenom, cnib, telephone) VALUES (?, ?, ?, ?)",
            (nom, prenom, cnib, telephone),
        )
        conn.commit()
    print(f"Abonné ajouté : {nom} {prenom}")
    audit_after_action(f"Abonné ajouté : {nom} {prenom}")



def ajouter_compteur(numero, abonne_id):
    with connect() as conn:
        conn.execute(
            "INSERT INTO compteurs (numero_compteur, abonne_id) VALUES (?, ?)",
            (numero, abonne_id),
        )
        conn.commit()
    print(f"Compteur {numero} lié à abonné {abonne_id}")
    audit_after_action(f"Compteur {numero} lié à abonné {abonne_id}")

    
def lister_compteurs():
    with connect() as conn:
        cur = conn.execute("""
            SELECT c.id, c.numero_compteur, a.nom, a.prenom, c.actif
            FROM compteurs c
            LEFT JOIN abonnes a ON c.abonne_id = a.id
        """)
        rows = cur.fetchall()
    for r in rows:
        print(r)

def menu_compteurs():
    print("=== Gestion des Compteurs ===")
    print("1. Init tables")
    print("2. Ajouter abonné")
    print("3. Ajouter compteur")
    print("4. Lister compteurs")
    print("0. Quitter")
    while True:
        choix = input("Choix: ").strip()
        if choix == "1":
            init_tables()
        elif choix == "2":
            ajouter_abonne(
                input("Nom: "), input("Prénom: "),
                input("CNIB: "), input("Téléphone: ")
            )
        elif choix == "3":
            ajouter_compteur(input("Numéro compteur: "), int(input("ID abonné: ")))
        elif choix == "4":
            lister_compteurs()
        elif choix == "0":
            break
        else:
            print("Option invalide.")

if __name__ == "__main__":
    menu_compteurs()
