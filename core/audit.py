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

    cur.execute("""
        SELECT f.id FROM factures f
        LEFT JOIN paiements p ON f.id = p.facture_id
        WHERE p.id IS NULL AND f.statut != 'payé'
    """)
    for row in cur.fetchall():
        log(f"Facture #{row[0]} sans paiement enregistré", "WARN")

    cur.execute("""
        SELECT id, facture_id FROM paiements
        WHERE facture_id NOT IN (SELECT id FROM factures)
    """)
    for row in cur.fetchall():
        log(f"Paiement #{row[0]} orphelin (facture {row[1]} inexistante)", "WARN")

    cur.execute("""
        SELECT f.id, f.montant_total, IFNULL(SUM(p.montant), 0)
        FROM factures f
        LEFT JOIN paiements p ON f.id = p.facture_id
        GROUP BY f.id
    """)
    for fid, total, paye in cur.fetchall():
        if paye > total:
            log(f"⚠ Facture #{fid} dépassement : payé {paye} > dû {total}", "ALERT")
        elif 0 < paye < total:
            log(f"⚠ Facture #{fid} partiellement payée : payé {paye}/{total}", "INFO")

    log("Vérification des factures terminée.\n")


def check_operations_paiements(conn):
    cur = conn.cursor()
    log("=== Vérification des opérations et paiements ===")

    cur.execute("""
        SELECT o.id, o.montant, IFNULL(SUM(po.montant), 0)
        FROM operations o
        LEFT JOIN paiements_operations po ON o.id = po.operation_id
        GROUP BY o.id
    """)
    for oid, total, paye in cur.fetchall():
        if paye == 0:
            log(f"Opération #{oid} sans paiement lié", "WARN")
        elif paye > total:
            log(f"⚠ Opération #{oid} dépassement : payé {paye} > dû {total}", "ALERT")
        elif paye < total:
            log(f"⚠ Opération #{oid} partiellement payée : payé {paye}/{total}", "INFO")

    log("Vérification des opérations terminée.\n")


def main():
    log("=== Audit Foragis v0.6 démarré ===")
    with connect() as conn:
        check_factures_paiements(conn)
        check_operations_paiements(conn)
    log("✅ Audit complet terminé.\n")


if __name__ == "__main__":
    main()
