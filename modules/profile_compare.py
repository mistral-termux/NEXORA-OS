#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import json
import socket
import subprocess
import shutil
import re

BASE = Path(__file__).resolve().parent.parent
STORE = BASE / "data" / "person_finder" / "observations.json"
REPORTS = BASE / "data" / "person_finder" / "reports"

def load_data():
    if not STORE.exists():
        return []
    try:
        data = json.loads(STORE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        print("Erreur : fichier d'observations illisible.")
        return []

def pause():
    input("\nEntrée pour continuer...")

def add_observation():
    data = load_data()
    pseudo = input("Pseudo public : ").strip().lstrip("@")
    platform = input("Plateforme : ").strip()
    url = input("URL publique du profil : ").strip()

    if not pseudo or not platform or not url.startswith(("https://", "http://")):
        print("Pseudo, plateforme et URL valide sont requis.")
        pause()
        return

    display_name = input("Nom d'affichage public (facultatif) : ").strip()
    bio = input("Biographie publique (facultatif) : ").strip()
    notes = input("Notes facultatives : ").strip()

    data.append({
        "date": datetime.now().astimezone().isoformat(timespec="seconds"),
        "pseudo_recherche": pseudo,
        "plateforme": platform,
        "url_source": url,
        "nom_affichage_public": display_name,
        "bio_publique": bio,
        "notes": notes,
        "identite_verifiee": False
    })

    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print("\nObservation enregistrée localement.")
    pause()

def view_observations(data=None):
    data = load_data() if data is None else data
    print("\n=== OBSERVATIONS PUBLIQUES ===")
    if not data:
        print("Aucune observation. Utilise l'option 1.")
    else:
        for i, item in enumerate(data, 1):
            print(f"\n[{i}] {item.get('pseudo_recherche', '?')}"
                  f" — {item.get('plateforme', '?')}")
            print("Nom public :", item.get("nom_affichage_public") or "Non renseigné")
            print("Bio :", item.get("bio_publique") or "Non renseignée")
            print("URL :", item.get("url_source", ""))
            print("Notes :", item.get("notes") or "Aucune")
    pause()

def normalize(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower().lstrip("@"))

def compare_profiles():
    data = load_data()
    if not data:
        print("Aucune observation à comparer.")
        pause()
        return

    query = input("Pseudo à comparer : ").strip()
    target = normalize(query)
    if not target:
        print("Pseudo vide.")
        pause()
        return

    matches = [
        item for item in data
        if normalize(item.get("pseudo_recherche", "")) == target
    ]

    print(f"\n=== COMPARAISON : {query} ===")
    if not matches:
        print("Aucune observation exacte trouvée.")
    else:
        for i, item in enumerate(matches, 1):
            print(f"\n--- Profil {i} ---")
            print("Plateforme :", item.get("plateforme", "Inconnue"))
            print("Pseudo saisi :", item.get("pseudo_recherche", ""))
            print("Nom public :", item.get("nom_affichage_public") or "Non renseigné")
            print("Bio publique :", item.get("bio_publique") or "Non renseignée")
            print("URL source :", item.get("url_source", ""))
            print("Date :", item.get("date", "Inconnue"))
            print("Notes :", item.get("notes") or "Aucune")

        print("\nAttention : des pseudos identiques ne prouvent pas une identité commune.")
        print("Vérifie chaque profil et ses sources indépendamment.")
    pause()

def export_report():
    data = load_data()
    if not data:
        print("Aucune observation à exporter.")
        pause()
        return

    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORTS / f"rapport_{stamp}.txt"

    lines = [
        "NEXORA OS — RAPPORT D'OBSERVATIONS PUBLIQUES",
        f"Généré le : {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "NOTE : ces observations ne confirment pas l'identité réelle d'une personne.",
        ""
    ]

    for i, item in enumerate(data, 1):
        lines.extend([
            f"[{i}] {item.get('pseudo_recherche', '?')}",
            f"Plateforme : {item.get('plateforme', '?')}",
            f"Nom public : {item.get('nom_affichage_public') or 'Non renseigné'}",
            f"Bio publique : {item.get('bio_publique') or 'Non renseignée'}",
            f"URL : {item.get('url_source', '')}",
            f"Date : {item.get('date', 'Inconnue')}",
            f"Notes : {item.get('notes') or 'Aucune'}",
            "-" * 40
        ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Rapport créé :", path)
    pause()

def network_diagnostic():
    print("\n=== DIAGNOSTIC RÉSEAU LOCAL ===")
    print("Nom de l'appareil :", socket.gethostname())

    try:
        addresses = sorted({
            item[4][0]
            for item in socket.getaddrinfo(socket.gethostname(), None)
            if item[0] in (socket.AF_INET, socket.AF_INET6)
            and not item[4][0].startswith("127.")
            and item[4][0] != "::1"
        })
        print("Adresses locales détectées :")
        if addresses:
            for address in addresses:
                print(" -", address)
        else:
            print("Aucune adresse locale détectée par Python.")
    except OSError as exc:
        print("Détection Python indisponible :", exc)

    ip_cmd = shutil.which("ip")
    if ip_cmd:
        for args, label in [
            (["-brief", "address"], "Interfaces et adresses"),
            (["route"], "Routes réseau")
        ]:
            print(f"\n{label} :")
            try:
                result = subprocess.run(
                    [ip_cmd] + args,
                    capture_output=True, text=True, timeout=5
                )
                print(result.stdout.strip() or result.stderr.strip() or "Aucune information.")
            except (OSError, subprocess.TimeoutExpired) as exc:
                print("Commande indisponible :", exc)
    else:
        print("Commande 'ip' indisponible dans cet environnement.")

    print("\nCe diagnostic porte sur cet environnement uniquement.")
    print("Il ne recherche pas l'adresse IP d'autres personnes.")
    pause()

def show():
    while True:
        print("\n=== NEXORA OS | PROFILE COMPARE v5 ===")
        print("[1] Ajouter une observation publique")
        print("[2] Consulter les observations")
        print("[3] Comparer les profils d'un pseudo")
        print("[4] Exporter un rapport TXT")
        print("[5] Diagnostic réseau local")
        print("[0] Retour au menu principal")

        choice = input("\nprofile-compare > ").strip()

        if choice == "0":
            return
        elif choice == "1":
            add_observation()
        elif choice == "2":
            view_observations()
        elif choice == "3":
            compare_profiles()
        elif choice == "4":
            export_report()
        elif choice == "5":
            network_diagnostic()
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    show()
