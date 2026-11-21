import socket
import urllib.request

def show():
    print("\n=== DIAGNOSTIC RÉSEAU ===")
    host = input("Hôte à tester [example.com] : ").strip() or "example.com"

    try:
        results = socket.getaddrinfo(host, None)
        print("DNS : OK")
        for result in results[:3]:
            print("Adresse :", result[4][0])
    except OSError as exc:
        print("DNS : ÉCHEC -", exc)

    try:
        req = urllib.request.Request(
            "https://example.com/",
            headers={"User-Agent": "NEXORA-OS/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            print("HTTPS : OK - code", response.status)
    except Exception as exc:
        print("HTTPS : indisponible -", exc)

    input("\nEntrée pour continuer...")
