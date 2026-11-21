from pathlib import Path
import os
import secrets
import sqlite3
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, g, flash, abort
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = Path(os.environ.get("NEXORA_DATA_DIR", str(ROOT / "data")))
PRIVATE_DIR = DATA_ROOT / "webpanel"
DB_PATH = PRIVATE_DIR / "users.sqlite3"
SECRET_PATH = PRIVATE_DIR / "secret_key.txt"

PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
os.chmod(PRIVATE_DIR, 0o700)

if not SECRET_PATH.exists():
    SECRET_PATH.write_text(secrets.token_hex(32), encoding="utf-8")
    os.chmod(SECRET_PATH, 0o600)

app = Flask(__name__)

IS_PRODUCTION = os.environ.get("NEXORA_ENV", "development").lower() == "production"
ENV_SECRET = os.environ.get("NEXORA_SECRET_KEY")

if IS_PRODUCTION and not ENV_SECRET:
    raise RuntimeError("NEXORA_SECRET_KEY doit être configurée en production.")

APP_SECRET = ENV_SECRET if IS_PRODUCTION else SECRET_PATH.read_text(encoding="utf-8").strip()

app.config.update(
    SECRET_KEY=APP_SECRET,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    MAX_CONTENT_LENGTH=16 * 1024,
)
CSRFProtect(app)


def connect_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'member')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


init_db()
os.chmod(DB_PATH, 0o600)


@app.before_request
def load_user():
    g.user = None
    uid = session.get("user_id")
    if uid is not None:
        with connect_db() as db:
            g.user = db.execute(
                "SELECT id, username, role FROM users WHERE id = ?",
                (uid,)
            ).fetchone()
        if g.user is None:
            session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; "
        "form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
    )
    return response


@app.route("/")
def index():
    if g.user:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with connect_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True
            return redirect(url_for("dashboard"))

        flash("Identifiants incorrects.", "error")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    observations_file = ROOT / "data" / "person_finder" / "observations.json"
    reports_dir = ROOT / "data" / "person_finder"
    txt_dir = reports_dir / "reports"

    observation_count = 0
    if observations_file.exists():
        try:
            import json
            data = json.loads(observations_file.read_text(encoding="utf-8"))
            observation_count = len(data) if isinstance(data, list) else 0
        except (ValueError, OSError):
            observation_count = 0

    json_reports = list(reports_dir.glob("*_report.json")) if reports_dir.exists() else []
    txt_reports = list(txt_dir.glob("rapport_*.txt")) if txt_dir.exists() else []

    return render_template(
        "dashboard.html",
        observations=observation_count,
        reports=len(json_reports) + len(txt_reports),
        user=g.user,
    )


@app.route("/admin/users", methods=["GET", "POST"])
@admin_required
def users():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "member")

        if not (3 <= len(username) <= 40):
            flash("Le nom doit contenir entre 3 et 40 caractères.", "error")
        elif not all(c.isalnum() or c in "_-." for c in username):
            flash("Utilise uniquement lettres, chiffres, point, tiret ou underscore.", "error")
        elif len(password) < 12:
            flash("Le mot de passe doit contenir au moins 12 caractères.", "error")
        elif role not in ("admin", "member"):
            flash("Rôle invalide.", "error")
        else:
            try:
                with connect_db() as db:
                    db.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, generate_password_hash(password), role)
                    )
                flash("Compte créé.", "success")
                return redirect(url_for("users"))
            except sqlite3.IntegrityError:
                flash("Ce nom d'utilisateur existe déjà.", "error")

    with connect_db() as db:
        all_users = db.execute(
            "SELECT id, username, role, created_at FROM users ORDER BY id"
        ).fetchall()

    return render_template("users.html", users=all_users)


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.errorhandler(403)
def forbidden(_error):
    return render_template(
        "message.html",
        title="Accès refusé",
        message="Ton compte n'a pas l'autorisation nécessaire."
    ), 403


if __name__ == "__main__":
    print("NEXORA WEB démarré sur http://127.0.0.1:5000")
    print("Arrêt : Ctrl+C")
    app.run(host="127.0.0.1", port=5000, debug=False)
