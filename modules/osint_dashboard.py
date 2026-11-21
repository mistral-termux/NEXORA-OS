#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import json

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "person_finder"
OBSERVATIONS = DATA / "observations.json"
REPORTS = DATA / "reports"

def read_observations():
    if not OBSERVATIONS.exists():
        return []
    try:
        data = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []

def get_reports():
    files = []
    if DATA.exists():
        files.extend(DATA.glob("*_report.json"))
    if REPORTS.exists():
        files.extend(REPORTS.glob("rapport_*.txt"))
    return sorted(
        (p for p in files if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

def show():
    while True:
        observations = read_observations()
        reports = get_reports()

        print("\n" + "=" * 46)
        print("       NEXORA OS | OSINT DASHBOARD")
        print("=" * 46)
        print("Date :", datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S"))
        print("\n--- STATISTIQUES ---")
        print("Observations publiques :", len(observations))
        print("Rapports enregistrés   :", len(reports))

        print("\n--- ÉTAT DES MODULES ---")
        modules = {
            "Person Finder": BASE / "modules" / "person_finder.py",
            "Profile Compare": BASE / "modules" / "profile_compare.py",
            "Diagnostic réseau": BASE / "modules" / "network.py",
            "Recherche sociale": BASE / "modules" / "social_finder.py",
        }
        for name, path in modules.items():
            status = "DISPONIBLE" if path.is_file() else "INTROUVABLE"
            print(f"{name:<22}: {status}")

        print("\n--- DERNIERS RAPPORTS ---")
        if not reports:
            print("Aucun rapport pour le moment.")
        else:
            for path in reports[:5]:
                size = path.stat().st_size
                modified = datetime.fromtimestamp(
                    path.stat().st_mtime
                ).astimezone().strftime("%d/%m/%Y %H:%M")
                print(f"- {path.name} ({size} octets, {modified})")

        print("\n[1] Afficher les observations")
        print("[2] Ouvrir le dossier des rapports")
        print("[0] Retour au menu principal")
        choice = input("\nosint-dashboard > ").strip()

        if choice == "0":
            return
        elif choice == "1":
            if not observations:
                print("Aucune observation enregistrée.")
            else:
                for i, item in enumerate(observations, 1):
                    print(f"\n[{i}] {item.get('pseudo_recherche', '?')}")
                    print("Plateforme :", item.get("plateforme", "?"))
                    print("Nom public :", item.get("nom_affichage_public") or "Non renseigné")
                    print("URL :", item.get("url_source", ""))
            input("\nEntrée pour continuer...")
        elif choice == "2":
            print("\nChemin du dossier :", REPORTS)
            print("Les rapports JSON de Person Finder se trouvent aussi dans :", DATA)
            input("\nEntrée pour continuer...")
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    show()
