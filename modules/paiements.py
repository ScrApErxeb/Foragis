import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_tables():
    schema_path = Path(__file__).resolve().parent.parent / "data" / "schema_update_v04b.sql"
    if not schema_path.exists():
        print("❌ Fichier de schéma introuvable.")
        return
    with connect() as conn, open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
        conn.commit()
    print("✅ Schéma appliqué et table 'paiements' prête.")

def enregistrer_paiement():
    try:
        facture_id = int(input("ID facture : "))
        montant = float(input("Montant payé : "))
    except ValueError:
        print("❌ Entrée invalide.")
        return

    with connect() as conn:
        cur = conn.cursor()

        # Vérifie que la colonne 'montant_total' existe
        cur.execute("PRAGMA table_info(factures)")
        colonnes = [c[1] for c in cur.fetchall()]
        if "montant_total" not in colonnes:
            print("❌ Erreur : la table 'factures' ne contient pas 'montant_total'.")
            print("👉 Applique d’abord le patch : schema_patch_factures_v04b.sql")
            return

        # Vérifie l’existence de la facture
        cur.execute("SELECT montant_total, statut FROM factures WHERE id=?", (facture_id,))
        facture = cur.fetchone()
        if not facture:
            print("❌ Facture introuvable.")
            return

        montant_total, statut = facture

        # Somme déjà payée
        cur.execute("SELECT SUM(montant) FROM paiements WHERE facture_id=?", (facture_id,))
        deja_paye = cur.fetchone()[0] or 0.0
        reste = montant_total - deja_paye

        # Refuse tout dépassement
        if montant > reste:
            print(f"⚠ Paiement refusé : {montant} dépasse le reste dû ({reste}).")
            return

        # Enregistre le paiement
        cur.execute(
            "INSERT INTO paiements (facture_id, montant) VALUES (?, ?)",
            (facture_id, montant)
        )

        # Met à jour le statut de la facture
        nouveau_total = deja_paye + montant
        etat = "payé" if nouveau_total >= montant_total else "partiel"
        cur.execute("UPDATE factures SET statut=? WHERE id=?", (etat, facture_id))
        conn.commit()

        print(f"✅ Paiement enregistré ({nouveau_total}/{montant_total}). État = {etat}.")

def lister_paiements():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(factures)")
        colonnes = [c[1] for c in cur.fetchall()]
        if "montant_total" not in colonnes:
            print("❌ Impossible d’afficher : colonne 'montant_total' absente.")
            return

        for row in cur.execute("""
        SELECT p.id, p.facture_id, p.montant, f.montant_total, f.statut
        FROM paiements p
        JOIN factures f ON f.id = p.facture_id
        ORDER BY p.id DESC
        """):
            print(f"[{row[0]}] Facture {row[1]} : {row[2]} / {row[3]} ({row[4]})")

def menu():
    print("=== Gestion des paiements ===")
    print("1. Init table")
    print("2. Enregistrer paiement")
    print("3. Lister paiements")
    print("0. Quitter")
    choix = input("Choix: ")
    if choix == "1":
        init_tables()
    elif choix == "2":
        enregistrer_paiement()
    elif choix == "3":
        lister_paiements()
    elif choix == "0":
        return

if __name__ == "__main__":
    while True:
        menu()
