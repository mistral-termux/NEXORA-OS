#!/usr/bin/env python3
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from modules.system import show as system_info
from modules.files import show as file_manager
from modules.network import show as network_check
from modules.person_finder import show as person_finder
from modules.osint_dashboard import show as osint_dashboard
from modules.profile_compare import show as profile_compare
from modules.social_finder import show as social_finder

CONFIG_FILE = BASE / "config" / "settings.json"
LOG_FILE = BASE / "logs" / "system.log"
DATA_DIR = BASE / "data"

# Couleurs ANSI : aucune bibliothèque externe requise.
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
DIM = "\033[2m"
RESET = "\033[0m"

def load_config():
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "name": "NEXORA OS",
            "version": "2.0.0",
            "edition": "Terminal Pro",
            "environment": "Debian Proot"
        }

CONFIG = load_config()

def log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {message}\n")

def pause(message="Appuie sur Entrée pour continuer..."):
    try:
        input(f"\n{DIM}{message}{RESET}")
    except (EOFError, KeyboardInterrupt):
        pass

def clear():
    os.system("clear")

def line(char="=", width=46):
    print(CYAN + char * width + RESET)

def header():
    clear()
    print(GREEN + r"""
 _   _ _____  __   _____  ____      _    OS
| \ | | ____| \ \ / / _ \/ ___|    / \
|  \| |  _|    \ V / | | \___ \   / _ \
| |\  | |___    | || |_| |___) | / ___ \
|_| \_|_____|   |_| \___/|____/ /_/   \_\
""" + RESET)
    print(f"{WHITE} {CONFIG.get('name', 'NEXORA OS')} "
          f"v{CONFIG.get('version', '2.0.0')}{RESET}")
    print(f" Edition : {CONFIG.get('edition', 'Terminal Pro')}")
    print(f" Environnement : Debian / Proot")
    line()

def dashboard():
    clear()
    header()
    system_info()


def show_logs():
    clear()
    header()
    print(f"\n{GREEN}       JOURNAL DES ÉVÉNEMENTS{RESET}\n")

    if not LOG_FILE.exists():
        print("Aucun journal disponible.")
    else:
        try:
            lines = LOG_FILE.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
            print("\n".join(lines[-40:]) or "Journal vide.")
        except OSError as exc:
            print(f"{RED}Erreur : {exc}{RESET}")

    pause()

def maintenance():
    while True:
        clear()
        header()
        print("\n  CENTRE DE MAINTENANCE\n")
        print(" [1] Vérifier les dépôts (apt update)")
        print(" [2] Installer les outils de base")
        print(" [3] Afficher les versions")
        print(" [0] Retour au menu principal")

        try:
            choice = input("\nnexora/maintenance > ").strip()
        except (EOFError, KeyboardInterrupt):
            return

        if choice == "0":
            return

        if choice == "1":
            print("\nMise à jour des index APT...")
            result = subprocess.run(["apt", "update"])
            log(f"apt update : code {result.returncode}")
            pause()
        elif choice == "2":
            packages = ["python3", "python3-venv", "curl", "nano",
                        "ca-certificates"]
            print("\nOutils prévus :", ", ".join(packages))
            confirm = input("Lancer l'installation avec APT ? [o/N] ")
            if confirm.lower() == "o":
                result = subprocess.run(["apt", "install", "-y"] + packages)
                log(f"Installation des outils : code {result.returncode}")
            else:
                print("Installation annulée.")
            pause()
        elif choice == "3":
            print("\nPython :", platform.python_version())
            for cmd in ("apt", "curl", "nano", "python3"):
                print(f"{cmd:10} : {shutil.which(cmd) or 'non trouvé'}")
            pause()
        else:
            print("Choix invalide.")
            pause()

def open_shell():
    clear()
    print(f"{GREEN}NEXORA OS — Shell Debian{RESET}")
    print("Tape 'exit' pour revenir à NEXORA OS.\n")
    log("Ouverture du shell Debian")
    try:
        subprocess.run(["/bin/bash"])
    except OSError as exc:
        print(f"Impossible d'ouvrir Bash : {exc}")
        pause()

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log("Démarrage de NEXORA OS 2.0")

    while True:
        header()
        print(f"\n{GREEN}  MENU PRINCIPAL{RESET}\n")
        print(" [1] Tableau de bord système")
        print(" [2] Gestionnaire de fichiers")
        print(" [3] Diagnostic réseau")
        print(" [4] Shell Debian")
        print(" [5] Journaux système")
        print(" [6] Centre de maintenance")
        print(" [7] Recherche de profils sociaux")
        print(" [8] Person Finder — profils publics")
        print(" [9] Profile Compare")
        print(" [10] Tableau de bord OSINT")
        print(" [0] Quitter NEXORA OS")
        line("-")

        try:
            choice = input(f"\n{GREEN}nexora@os{RESET} > ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "0"

        try:
            if choice == "1":
                dashboard()
            elif choice == "2":
                file_manager(DATA_DIR)
            elif choice == "3":
                network_check()
            elif choice == "4":
                open_shell()
            elif choice == "5":
                show_logs()
            elif choice == "6":
                maintenance()
            elif choice == "7":
                social_finder()
            elif choice == "8":
                person_finder()
            elif choice == "9":
                profile_compare()
            elif choice == "10":
                osint_dashboard()
            elif choice == "0":
                log("Arrêt de NEXORA OS")
                print(f"\n{YELLOW}NEXORA OS fermé. Debian reste actif.{RESET}")
                break
            else:
                print(f"{RED}Option inconnue.{RESET}")
                pause()
        except KeyboardInterrupt:
            print("\nOpération interrompue.")
            log("Opération interrompue par l'utilisateur")
            pause()

if __name__ == "__main__":
    main()
