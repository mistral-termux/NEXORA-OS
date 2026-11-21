#!/usr/bin/env python3
from urllib.parse import quote
import subprocess
import shutil
import webbrowser

PLATFORMS = {
    "1": ("TikTok", "https://www.tiktok.com/@{}"),
    "2": ("GitHub", "https://github.com/{}"),
    "3": ("Reddit", "https://www.reddit.com/user/{}/"),
    "4": ("Discord — recherche web",
          "https://www.google.com/search?q={}+site%3Adiscord.com"),
}

def show():
    print("\n=== NEXORA OS | SOCIAL FINDER ===")
    username = input("Pseudo à rechercher (sans @) : ").strip().lstrip("@")

    if not username or any(c.isspace() for c in username):
        print("Pseudo invalide.")
        input("Appuie sur Entrée pour revenir...")
        return

    print("\n[1] TikTok")
    print("[2] GitHub")
    print("[3] Reddit")
    print("[4] Discord — recherche web")
    print("[5] Toutes les plateformes")
    print("[0] Retour")

    choice = input("\n social-finder > ").strip()

    if choice == "0":
        return
    elif choice == "5":
        selected = list(PLATFORMS.keys())
    elif choice in PLATFORMS:
        selected = [choice]
    else:
        print("Choix invalide.")
        input("Appuie sur Entrée pour revenir...")
        return

    encoded = quote(username, safe="")
    links = []

    print("\n=== LIENS DE RECHERCHE ===")
    for key in selected:
        name, template = PLATFORMS[key]
        url = template.format(encoded)
        links.append((name, url))
        print(f"\n{name} :\n{url}")

    print("\nLes résultats doivent être vérifiés manuellement.")
    answer = input("\nOuvrir les liens dans le navigateur ? [o/N] ").strip().lower()

    if answer == "o":
        for name, url in links:
            try:
                opener = shutil.which("termux-open-url")
                if opener:
                    result = subprocess.run([opener, url], check=False)
                    if result.returncode != 0:
                        print(f"Échec de l'ouverture de {name}.")
                else:
                    print("Passerelle Android non trouvée dans Debian.")
                    print("Lien à ouvrir manuellement :", url)
            except Exception as exc:
                print(f"Impossible d'ouvrir {name} : {exc}")
        print("Si aucun navigateur ne s'ouvre, utilise les liens affichés.")

    input("\nAppuie sur Entrée pour revenir au menu...")
