#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
import json
import shutil
import subprocess

BASE = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE / "data" / "person_finder"

PLATFORMS = {
    "1": ("TikTok", "https://www.tiktok.com/@{}"),
    "2": ("Instagram", "https://www.instagram.com/{}/"),
    "3": ("YouTube", "https://www.youtube.com/results?search_query={}"),
    "4": ("Discord - recherche Web",
          "https://www.google.com/search?q={}+site%3Adiscord.com"),
    "5": ("GitHub", "https://github.com/{}"),
    "6": ("Reddit", "https://www.reddit.com/user/{}/"),
    "7": ("Recherche Web", "https://www.google.com/search?q={}"),
}

def pause():
    input("\nEntrée pour revenir...")

def open_url(url):
    opener = shutil.which("termux-open-url")
    if opener:
        result = subprocess.run([opener, url], check=False)
        if result.returncode == 0:
            return
    print("Ouverture non confirmée. Lien :", url)

def save_report(username, results, note=""):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"{stamp}_report.json"
    report = {
        "pseudo_recherche": username,
        "date": datetime.now().astimezone().isoformat(timespec="seconds"),
        "note_utilisateur": note,
        "avertissement": (
            "Les résultats sont des pistes publiques. "
            "Un pseudo commun ne prouve pas une identité."
        ),
        "resultats": results,
    }
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nRapport enregistré : {path}")

def new_search():
    print("\n=== PERSON FINDER v3 | NOUVELLE RECHERCHE ===")
    username = input("Pseudo public : ").strip().lstrip("@")
    if not username or len(username) > 100 or any(c.isspace() for c in username):
        print("Pseudo invalide.")
        pause()
        return

    print("\n[1] TikTok  [2] Instagram  [3] YouTube")
    print("[4] Discord [5] GitHub     [6] Reddit")
    print("[7] Recherche Web [8] Toutes les recherches")
    choice = input("\nChoix > ").strip()

    if choice == "8":
        keys = list(PLATFORMS)
    elif choice in PLATFORMS:
        keys = [choice]
    else:
        print("Choix invalide.")
        pause()
        return

    encoded = quote(username, safe="")
    results = []
    for key in keys:
        name, template = PLATFORMS[key]
        url = template.format(encoded)
        results.append({
            "plateforme": name,
            "url": url,
            "statut": "À vérifier manuellement",
            "notes": ""
        })
        print(f"\n{name}: {url}")

    if input("\nOuvrir tous les liens ? [o/N] ").strip().lower() == "o":
        for item in results:
            open_url(item["url"])

    note = input("\nNote de vérification facultative : ").strip()
    save_report(username, results, note)
    pause()

def history():
    print("\n=== HISTORIQUE PERSON FINDER ===")
    files = sorted(
        REPORT_DIR.glob("*_report.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    ) if REPORT_DIR.exists() else []

    if not files:
        print("Aucun rapport enregistré.")
        pause()
        return

    for index, path in enumerate(files[:30], 1):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            print(f"[{index}] {data.get('date', '?')} — "
                  f"{data.get('pseudo_recherche', '?')}")
        except (OSError, json.JSONDecodeError):
            print(f"[{index}] {path.name} — rapport illisible")

    choice = input("\nNuméro du rapport à afficher, ou Entrée pour revenir : ").strip()
    if not choice:
        return
    if not choice.isdigit() or not 1 <= int(choice) <= min(30, len(files)):
        print("Numéro invalide.")
        pause()
        return

    path = files[int(choice) - 1]
    print("\n" + path.read_text(encoding="utf-8"))
    pause()

def show():
    while True:
        print("\n=== NEXORA OS | PERSON FINDER v3 ===")
        print("[1] Nouvelle recherche")
        print("[2] Historique des rapports")
        print("[0] Retour au menu principal")
        choice = input("\nperson-finder > ").strip()

        if choice == "0":
            return
        elif choice == "1":
            new_search()
        elif choice == "2":
            history()
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    show()
