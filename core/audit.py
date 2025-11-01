# core/audit.py
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "foragis.db"
LOG_PATH = Path(__file__).resolve().parent.parent / "foragis_env" / "logs.txt"


def connect():
    return sqlite3.connect(DB_PATH)


def log(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}"
    print(entry)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def check_factures_paiements(conn):
    cur = conn.cursor()
    log("=== Vérification des factures et paiements ===")

    # Vérifie factures sans paiement
    cur.execute("""
        SELECT f.id FROM factures f
        LEFT JOIN paiements p ON f.id = p.facture_id
        WHERE p.id IS NULL AND f.statut != 'payé'
    """)
    for row in cur.fetchall():
        log(f"Facture #{row[0]} sans paiement enregistré", "WARN")

    # Paiements sans facture valide
    cur.execute("""
        SELECT id, facture_id FROM paiements
        WHERE facture_id NOT IN (SELECT id FROM factures)
    """)
    for row in cur.fetchall():
        log(f"Paiement #{row[0]} orphelin (facture {row[1]} inexistante)", "WARN")

    # Dépassements de paiement
    cur.execute("""
        SELECT f.id, f.montant_total, IFNULL(SUM(p.montant), 0)
        FROM factures f
        LEFT JOIN paiements p ON f.id = p.facture_id
        GROUP BY f.id
        HAVING SUM(p.montant) > f.montant_total
    """)
    for row in cur.fetchall():
        log(f"⚠ Facture #{row[0]} dépassement : payé {row[2]} > dû {row[1]}", "ALERT")

    log("Vérification des factures terminée.\n")


def check_operations_paiements(conn):
    cur = conn.cursor()
    log("=== Vérification des opérations et paiements ===")

    # Opérations sans paiement
    cur.execute("""
        SELECT o.id FROM operations o
        LEFT JOIN paiements_operations po ON o.id = po.operation_id
        WHERE po.id IS NULL
    """)
    for row in cur.fetchall():
        log(f"Opération #{row[0]} sans paiement lié", "WARN")

    # Paiements opérations sans opération
    cur.execute("""
        SELECT id, operation_id FROM paiements_operations
        WHERE operation_id NOT IN (SELECT id FROM operations)
    """)
    for row in cur.fetchall():
        log(f"Paiement opération #{row[0]} orphelin (operation {row[1]} inexistante)", "WARN")

    # Dépassements
    cur.execute("""
        SELECT o.id, o.montant, IFNULL(SUM(po.montant), 0)
        FROM operations o
        LEFT JOIN paiements_operations po ON o.id = po.operation_id
        GROUP BY o.id
        HAVING SUM(po.montant) > o.montant
    """)
    for row in cur.fetchall():
        log(f"⚠ Opération #{row[0]} dépassement : payé {row[2]} > dû {row[1]}", "ALERT")

    log("Vérification des opérations terminée.\n")


def main():
    log("=== Audit Foragis v0.6 démarré ===")
    with connect() as conn:
        check_factures_paiements(conn)
        check_operations_paiements(conn)
    log("✅ Audit complet terminé.\n")


if __name__ == "__main__":
    main()
