import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "foragis.db"
LOG_PATH = Path(__file__).resolve().parents[1] / "foragis_env" / "logs.txt"


def connect():
    return sqlite3.connect(DB_PATH)


def log(message, level="INFO"):
    """Écrit un message dans la console et dans le journal."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}"
    print(entry)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def validate_id_exists(table, record_id):
    """Vérifie que l’ID existe dans la table."""
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM {table} WHERE id=?", (record_id,))
        if not cur.fetchone():
            log(f"❌ ID {record_id} inexistant dans {table}", "ERROR")
            return False
    return True


def validate_positive_amount(amount):
    """Vérifie que le montant est numérique et positif."""
    try:
        value = float(amount)
        if value <= 0:
            log(f"❌ Montant invalide ({value})", "ERROR")
            return False
        return True
    except ValueError:
        log(f"❌ Entrée non numérique ({amount})", "ERROR")
        return False


def validate_schema_columns(table, required_cols):
    """Vérifie que certaines colonnes existent avant exécution."""
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cur.fetchall()]
        missing = [c for c in required_cols if c not in cols]
        if missing:
            log(f"❌ Colonnes manquantes dans {table} : {', '.join(missing)}", "ERROR")
            return False
    return True
