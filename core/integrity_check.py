# core/integrity_check.py
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"
LOG_PATH = Path(__file__).resolve().parents[1] / "foragis_env" / "logs.txt"


def connect():
    return sqlite3.connect(DB_PATH)


def log(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}"
    print(entry)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def check_table_exists(table):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        if not cur.fetchone():
            log(f"❌ Table manquante : {table}", "ERROR")
            return False
    return True


def check_column_exists(table, column):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cur.fetchall()]
        if column not in cols:
            log(f"❌ Colonne manquante : {table}.{column}", "ERROR")
            return False
    return True


def check_foreign_relations():
    log("=== Vérification des relations entre tables ===")
    required = [
        ("paiements", "facture_id", "factures"),
        ("paiements_operations", "operation_id", "operations"),
    ]
    for table, col, ref in required:
        if check_table_exists(table) and check_table_exists(ref):
            with connect() as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT DISTINCT {col} FROM {table}")
                ids = [r[0] for r in cur.fetchall()]
                cur.execute(f"SELECT id FROM {ref}")
                ref_ids = {r[0] for r in cur.fetchall()}
                for i in ids:
                    if i not in ref_ids:
                        log(f"⚠ Incohérence : {table}.{col}={i} sans {ref}", "WARN")


def check_integrity():
    log("=== Audit d’intégrité Foragis ===")

    # Étape 1 : structure minimale
    for table in ["factures", "paiements", "operations", "paiements_operations"]:
        check_table_exists(table)

    # Étape 2 : colonnes clés
    checks = [
        ("factures", "montant_total"),
        ("paiements", "montant"),
        ("operations", "montant"),
        ("paiements_operations", "montant"),
    ]
    for table, col in checks:
        check_column_exists(table, col)

    # Étape 3 : cohérences croisées
    check_foreign_relations()

    log("✅ Vérification d’intégrité terminée.\n")


if __name__ == "__main__":
    check_integrity()
