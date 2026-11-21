import getpass
import os
import re
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
data_root = Path(os.environ.get("NEXORA_DATA_DIR", str(ROOT / "data")))
private_dir = data_root / "webpanel"
db_path = private_dir / "users.sqlite3"

if not db_path.exists():
    raise SystemExit("Base absente : lance d'abord webpanel/app.py une fois.")

username = input("Nom du compte administrateur : ").strip()
if not re.fullmatch(r"[A-Za-z0-9_.-]{3,40}", username):
    raise SystemExit("Nom invalide : 3 à 40 caractères, lettres, chiffres, . _ -")

password = getpass.getpass("Mot de passe (12 caractères minimum) : ")
confirm = getpass.getpass("Confirme le mot de passe : ")

if len(password) < 12:
    raise SystemExit("Mot de passe trop court.")
if password != confirm:
    raise SystemExit("Les mots de passe ne correspondent pas.")

with sqlite3.connect(db_path) as db:
    count = db.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'admin'"
    ).fetchone()[0]
    if count:
        raise SystemExit("Un administrateur existe déjà. Aucun compte créé.")
    try:
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            (username, generate_password_hash(password))
        )
    except sqlite3.IntegrityError:
        raise SystemExit("Ce nom d'utilisateur existe déjà.")

os.chmod(db_path, 0o600)
print("Compte administrateur créé.")
