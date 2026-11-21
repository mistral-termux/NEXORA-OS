import os
import sys
import json
import shutil
import socket
import platform
import subprocess
from pathlib import Path

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run(args):
    try:
        p = subprocess.run(
            args, capture_output=True, text=True, timeout=5
        )
        return p.stdout.strip() or p.stderr.strip() or "Indisponible"
    except (OSError, subprocess.TimeoutExpired):
        return "Indisponible"

def section(name):
    print(f"\n{CYAN}====== {name} ======{RESET}")

def show():
    home = Path.home()
    base = Path(__file__).resolve().parent.parent

    os.system("clear")
    print(GREEN + r"""
 _   _ _____  __   _____  ____      _    OS
| \ | | ____| \ \ / / _ \/ ___|    / \
|  \| |  _|    \ V / | | \___ \   / _ \
| |\  | |___    | || |_| |___) | / ___ \
|_| \_|_____|   |_| \___/|____/ /_/   \_\
""" + RESET)

    section("SYSTEME")
    print("OS             :", platform.system())
    print("Version noyau  :", platform.release())
    print("Architecture   :", platform.machine())
    print("Python         :", sys.version.split()[0])
    print("Exécutable     :", sys.executable)
    print("Utilisateur    :", os.environ.get("USER", "inconnu"))
    print("Dossier HOME   :", home)

    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if line.startswith("PRETTY_NAME="):
                print("Distribution   :", line.split("=", 1)[1].strip('"'))
                break
    except OSError:
        print("Distribution   : inconnue")

    section("PROCESSEUR")
    print("CPU logiques   :", run(["getconf", "_NPROCESSORS_ONLN"]))
    try:
        cpu = next(
            (x.split(":", 1)[1].strip()
             for x in Path("/proc/cpuinfo").read_text().splitlines()
             if x.lower().startswith("model name")),
            "Modèle non exposé"
        )
        print("Modèle         :", cpu)
    except OSError:
        print("Modèle         : indisponible")

    section("MEMOIRE VISIBLE")
    try:
        mem = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, _, value = line.partition(":")
            if value.strip().endswith("kB"):
                mem[key] = int(value.strip().split()[0]) // 1024
        print("Mémoire totale :", mem.get("MemTotal", "N/D"), "Mo")
        print("Mémoire libre disponible :",
              mem.get("MemAvailable", "N/D"), "Mo")
    except (OSError, ValueError):
        print("Mémoire : indisponible")

    try:
        seconds = float(Path("/proc/uptime").read_text().split()[0])
        print(f"Uptime visible : {int(seconds // 3600)} h "
              f"{int(seconds % 3600 // 60)} min")
    except (OSError, ValueError):
        print("Uptime : indisponible")

    section("STOCKAGE")
    try:
        total, used, free = shutil.disk_usage(home)
        gb = 1024 ** 3
        print(f"Total          : {total / gb:.2f} Go")
        print(f"Utilisé        : {used / gb:.2f} Go")
        print(f"Libre          : {free / gb:.2f} Go")
    except OSError:
        print("Stockage : indisponible")
    print(run(["df", "-h", str(home)]))

    section("RESEAU")
    print("Nom hôte       :", socket.gethostname())
    print("Interfaces IP :")
    print(run(["ip", "-brief", "address"]))
    try:
        addresses = sorted({
            item[4][0] for item in socket.getaddrinfo(
                socket.gethostname(), None
            )
        })
        print("Adresses hôte  :", ", ".join(addresses) or "Aucune")
    except OSError:
        print("Adresses hôte  : indisponibles")
    try:
        socket.getaddrinfo("example.com", 443)
        print("Résolution DNS : OK")
    except OSError:
        print("Résolution DNS : échec")

    section("OUTILS")
    for name in (
        "python", "python3", "pip", "pip3", "curl", "wget",
        "git", "nano", "7z", "unzip", "tar", "apt", "proot",
        "docker", "ssh"
    ):
        print(f"{name:12} : {shutil.which(name) or 'non installé'}")

    section("ENVIRONNEMENT PYTHON")
    print("Virtualenv actif :", os.environ.get("VIRTUAL_ENV", "aucun"))
    for name in ("venv_brixhub", "venv_nexora"):
        path = home / name
        if path.is_dir():
            print(f"Environnement trouvé : {path}")

    section("NEXORA OS")
    print("Dossier :", base)
    config = base / "config" / "settings.json"
    try:
        settings = json.loads(config.read_text(encoding="utf-8"))
        print("Nom     :", settings.get("name", "NEXORA OS"))
        print("Version :", settings.get("version", "inconnue"))
        print("Édition :", settings.get("edition", "inconnue"))
    except (OSError, ValueError):
        print("Configuration : indisponible")

    for folder in ("core", "modules", "config", "logs", "data"):
        print(f"{folder:10} :",
              "OK" if (base / folder).is_dir() else "absent")

    print(f"\n{YELLOW}Les données affichées sont celles accessibles "
          "depuis Termux ou Proot.{RESET}")
    try:
        input("\nEntrée pour revenir au menu...")
    except (EOFError, KeyboardInterrupt):
        pass
