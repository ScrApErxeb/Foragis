import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "foragis.db"
LOG_PATH = BASE_DIR / "foragis_env" / "logs.txt"


def log(msg):
    LOG_PATH.parent.mkdir(exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def fix_table(table_name, ref_table, ref_field):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        if table_name == "paiements":
            cur.execute("""
                SELECT p.facture_id, SUM(p.montant) AS total_paye, f.montant AS du
                FROM paiements p
                JOIN factures f ON p.facture_id = f.id
                GROUP BY p.facture_id
                HAVING total_paye > f.montant
            """)
        else:  # paiements_operations
            cur.execute("""
                SELECT p.operation_id, SUM(p.montant) AS total_paye, o.montant AS du
                FROM paiements_operations p
                JOIN operations o ON p.operation_id = o.id
                GROUP BY p.operation_id
                HAVING total_paye > o.montant
            """)


        anomalies = cur.fetchall()
        if not anomalies:
            log(f"Aucune anomalie trouvée dans {table_name}.")
            return

        log(f"=== Correction anomalies {table_name} ===")
        for ref_id, total_paye, du in anomalies:
            excess = total_paye - du
            log(f"ID {ref_id} : payé {total_paye} > dû {du} (excédent {excess})")

            # On réduit le dernier paiement du montant excédentaire
            if table_name == "paiements":
                cur.execute(
                    "SELECT id, montant FROM paiements WHERE facture_id=? ORDER BY date_paiement DESC LIMIT 1",
                    (ref_id,)
                )
            else:
                cur.execute(
                    "SELECT id, montant FROM paiements_operations WHERE operation_id=? ORDER BY date_paiement DESC LIMIT 1",
                    (ref_id,)
                )

            last = cur.fetchone()
            if last:
                pid, montant = last
                new_montant = max(0, montant - excess)
                cur.execute(f"UPDATE {table_name} SET montant=? WHERE id=?", (new_montant, pid))
                conn.commit()
                log(f"→ Paiement {pid} ajusté de {montant} à {new_montant}")
            else:
                log(f"⚠ Impossible de corriger {table_name} ref {ref_id} (aucun paiement trouvé)")

        log(f"Fin correction {table_name}.\n")


def main():
    print("=== Correction des paiements anormaux ===")
    fix_table("paiements", "factures", "facture_id")
    fix_table("paiements_operations", "operations", "operation_id")
    print("✅ Vérification et corrections terminées. Voir logs pour détails.")


if __name__ == "__main__":
    main()
