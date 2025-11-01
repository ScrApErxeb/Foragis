# core/audit_manager.py
import sqlite3
from pathlib import Path
from datetime import datetime
from core.validator import log

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"
LOG_PATH = Path(__file__).resolve().parents[1] / "foragis_env" / "logs.txt"


def connect():
    return sqlite3.connect(DB_PATH)


def run_factures_audit(conn):
    """Contrôle la cohérence des factures et paiements liés."""
    cur = conn.cursor()
    log("=== Audit factures ===")

    cur.execute("""
        SELECT f.id, f.montant_total, IFNULL(SUM(p.montant), 0)
        FROM factures f
        LEFT JOIN paiements p ON f.id = p.facture_id
        GROUP BY f.id
    """)

    for fid, total, paye in cur.fetchall():
        if paye == 0:
            log(f"⚠ Facture {fid} sans paiement.", "WARN")
        elif paye < total:
            log(f"⚠ Facture {fid} partielle ({paye}/{total}).", "INFO")
        elif paye > total:
            log(f"❌ Facture {fid} excédentaire ({paye}>{total}).", "ALERT")

    log("Audit factures terminé.\n")


def run_operations_audit(conn):
    """Contrôle la cohérence des opérations et paiements associés."""
    cur = conn.cursor()
    log("=== Audit opérations ===")

    cur.execute("""
        SELECT o.id, o.montant, IFNULL(SUM(po.montant), 0)
        FROM operations o
        LEFT JOIN paiements_operations po ON o.id = po.operation_id
        GROUP BY o.id
    """)

    for oid, total, paye in cur.fetchall():
        if paye == 0:
            log(f"⚠ Opération {oid} sans paiement.", "WARN")
        elif paye < total:
            log(f"⚠ Opération {oid} partielle ({paye}/{total}).", "INFO")
        elif paye > total:
            log(f"❌ Opération {oid} excédentaire ({paye}>{total}).", "ALERT")

    log("Audit opérations terminé.\n")


def full_audit():
    """Exécute tous les audits et écrit dans le journal."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"=== Audit global Foragis lancé ({ts}) ===")

    with connect() as conn:
        run_factures_audit(conn)
        run_operations_audit(conn)

    log("✅ Audit global terminé.\n")


def audit_after_action(action_name: str):
    """Audit automatique après une action critique."""
    log(f"--- Audit automatique déclenché après : {action_name} ---")
    full_audit()


if __name__ == "__main__":
    full_audit()
