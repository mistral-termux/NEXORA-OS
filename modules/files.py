from pathlib import Path

def show(data_dir):
    data_dir = Path(data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    while True:
        print("\n=== NEXORA FILES ===")
        print("Dossier :", data_dir)
        try:
            entries = sorted(data_dir.iterdir())
            if not entries:
                print("(Dossier vide)")
            for entry in entries:
                kind = "DOSSIER" if entry.is_dir() else "FICHIER"
                print(f"[{kind}] {entry.name}")
        except OSError as exc:
            print("Erreur :", exc)

        print("\n1. Créer un dossier")
        print("2. Créer un fichier texte")
        print("0. Retour")
        choice = input("nexora/files > ").strip()

        if choice == "0":
            return
        elif choice == "1":
            name = input("Nom du dossier : ").strip()
            if name and name not in (".", "..") and "/" not in name:
                (data_dir / name).mkdir(exist_ok=True)
        elif choice == "2":
            name = input("Nom du fichier : ").strip()
            if name and name not in (".", "..") and "/" not in name:
                content = input("Contenu : ")
                target = data_dir / name
                if target.exists():
                    print("Fichier déjà existant : opération annulée.")
                else:
                    target.write_text(content + "\n", encoding="utf-8")
