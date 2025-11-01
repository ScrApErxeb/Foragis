import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "foragis.db"

def connect():
    return sqlite3.connect(DB_PATH)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def init_users_table():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'secretaire')) NOT NULL DEFAULT 'secretaire'
        )
        """)
        conn.commit()
    print("✅ Table 'users' prête.")

def create_user(username: str, password: str, role: str = "secretaire"):
    with connect() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hash_password(password), role)
            )
            conn.commit()
            print(f"✅ Utilisateur '{username}' créé avec rôle '{role}'.")
        except sqlite3.IntegrityError:
            print("❌ Nom d’utilisateur déjà existant.")

def login():
    username = input("Nom d’utilisateur : ").strip()
    password = input("Mot de passe : ").strip()

    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash, role FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if not user:
            print("❌ Utilisateur introuvable.")
            return None

        hashed, role = user
        if verify_password(password, hashed):
            print(f"✅ Connecté en tant que {role}.")
            return {"username": username, "role": role}
        else:
            print("❌ Mot de passe incorrect.")
            return None

def menu():
    print("=== Authentification Foragis ===")
    print("1. Init table users")
    print("2. Créer utilisateur")
    print("3. Connexion")
    print("0. Quitter")
    choix = input("Choix : ").strip()
    if choix == "1":
        init_users_table()
    elif choix == "2":
        username = input("Nom d’utilisateur : ")
        password = input("Mot de passe : ")
        role = input("Rôle (admin/secretaire) : ").strip() or "secretaire"
        create_user(username, password, role)
    elif choix == "3":
        login()
    elif choix == "0":
        return

if __name__ == "__main__":
    while True:
        menu()
