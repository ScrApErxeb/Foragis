from pathlib import Path
import sqlite3
from datetime import datetime

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "foragis_env" / "logs.txt"

STRUCTURE = [
    "core",
    "modules",
    "data",
    "foragis_env",
]


def log(message: str):
    timestamp = datetime.now().isoformat(timespec="seconds")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)


def create_folders():
    for folder in STRUCTURE:
        path = BASE_DIR / folder
        path.mkdir(exist_ok=True)
        log(f"Dossier créé : {path}")


def create_db():
    db_path = BASE_DIR / "data" / "foragis.db"
    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        conn.close()
        log(f"Base créée : {db_path}")
    else:
        log("Base déjà existante.")


def create_init_files():
    for folder in ["core", "modules"]:
        init_file = BASE_DIR / folder / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
            log(f"__init__.py ajouté dans {folder}")


def create_env_files():
    env_dir = BASE_DIR / "foragis_env"
    files = {
        "logs.txt": "# Journal d’activité Foragis\n",
        "config.yaml": "# Configuration par défaut\nAPP_MODE: dev\nDB_PATH: data/foragis.db\n",
        "README.md": "# Dossier environnement Foragis\nContient logs, sauvegardes, et fichiers temporaires.\n",
        ".env": "APP_MODE=dev\nDB_PATH=data/foragis.db\n",
    }
    for name, content in files.items():
        f = env_dir / name
        if not f.exists():
            f.write_text(content)
            log(f"Fichier créé : {f}")


def create_gitignore():
    gitignore_path = BASE_DIR / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# Foragis .gitignore\n"
            "__pycache__/\n"
            "*.pyc\n"
            "*.db\n"
            "foragis_env/logs.txt\n"
            "foragis_env/*.bak\n"
            "foragis_env/*.tmp\n"
            "foragis_env/*.log\n"
            "data/*.db\n"
            ".env\n"
        )
        log("Fichier .gitignore créé.")
    else:
        log(".gitignore déjà existant.")


def verify_setup():
    checks = {
        "core": (BASE_DIR / "core").exists(),
        "modules": (BASE_DIR / "modules").exists(),
        "data": (BASE_DIR / "data").exists(),
        "foragis_env": (BASE_DIR / "foragis_env").exists(),
        "database": (BASE_DIR / "data" / "foragis.db").exists(),
        "gitignore": (BASE_DIR / ".gitignore").exists(),
    }
    ok = all(checks.values())
    if ok:
        log("✅ Vérification : tous les composants sont présents et valides.")
    else:
        log("❌ Vérification : éléments manquants.")
        for k, v in checks.items():
            if not v:
                log(f"   - Manquant : {k}")
    return ok


def main():
    print("=== Initialisation Foragis V00 ===")
    create_folders()
    create_init_files()
    create_db()
    create_env_files()
    create_gitignore()
    if verify_setup():
        print("✅ Tous les tests de structure et fichiers sont passés avec succès.")
    else:
        print("⚠ Des éléments manquent. Voir foragis_env/logs.txt.")
    log("Initialisation complète.\n")


if __name__ == "__main__":
    main()
