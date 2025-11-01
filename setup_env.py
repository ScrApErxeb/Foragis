import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
VENV_DIR = BASE_DIR / "foragis_env" / "venv"
REQ_FILE = BASE_DIR / "requirements.txt"

def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Erreur: commande échouée -> {cmd}")
        sys.exit(1)

def main():
    print("=== Configuration environnement Foragis ===")
    if not VENV_DIR.exists():
        run(f"{sys.executable} -m venv {VENV_DIR}")
        print("Environnement virtuel créé.")
    else:
        print("Environnement virtuel déjà présent.")
    pip_path = VENV_DIR / "Scripts" / "pip.exe" if sys.platform == "win32" else VENV_DIR / "bin" / "pip"
    run(f"{pip_path} python.exe -m pip install --upgrade pip")
    run(f"{pip_path} install -r {REQ_FILE}")
    print("✅ Environnement prêt.")

if __name__ == "__main__":
    main()
