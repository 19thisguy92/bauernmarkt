import json
import re
from datetime import datetime
print("Systemzeit:", datetime.now())

import requests

URL = "http://www.bauernmarkt-wels.at/"

print("Lade Homepage...")

response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

response.raise_for_status()

html = response.text

print("Homepage geladen.")

# --------------------------------------------------------
# Menü-Slider suchen
# --------------------------------------------------------

marker = "gabis_menue_logo.png"

pos = html.find(marker)

if pos == -1:
    raise Exception("Menülogo nicht gefunden!")

bereich = html[pos:pos + 8000]

print("Menübereich gefunden.")

# --------------------------------------------------------
# Datum suchen
# --------------------------------------------------------

datum_match = re.search(
    r"Freitag,\s*([0-9]{1,2}\.\s*[A-Za-zÄÖÜäöü]+\s*[0-9]{4})",
    bereich
)

if not datum_match:
    raise Exception("Kein Datum gefunden!")

datum = datum_match.group(1)

print("Datum:", datum)

# --------------------------------------------------------
# Menü suchen
# --------------------------------------------------------

menu_match = re.search(
    r"layer-4.*?<rs-bg-elem.*?</rs-bg-elem>(.*?)</rs-layer>",
    bereich,
    re.S
)

if not menu_match:
    raise Exception("Menü nicht gefunden!")

menu_html = menu_match.group(1)

menu_html = menu_html.replace("<br />", "\n")
menu_html = menu_html.replace("<br/>", "\n")
menu_html = menu_html.replace("<br>", "\n")

menu_html = re.sub(r"<.*?>", "", menu_html)

menue = []

for zeile in menu_html.splitlines():
    zeile = zeile.strip()

    if not zeile:
        continue

    if zeile.startswith("+"):
        zeile = zeile[1:].strip()

    menue.append(zeile)

print()
print("Gefundenes Menü:")

for eintrag in menue:
    print("-", eintrag)

# --------------------------------------------------------
# JSON erzeugen
# --------------------------------------------------------

daten = {
    "restaurant": "Bauernmarkt Wels",
    "url": URL,
    "updated": datetime.now().isoformat(),
    "menu_date": f"Freitag, {datum}",
    "current": True,
    "menu": menue
}

with open("menu.json", "w", encoding="utf-8") as f:
    json.dump(
        daten,
        f,
        ensure_ascii=False,
        indent=4
    )

with open("menu.txt", "w", encoding="utf-8") as f:
    f.write("Bauernmarkt Wels\n\n")
    f.write(f"Freitag, {datum}\n\n")

    for eintrag in menue:
        f.write(f"• {eintrag}\n")

print()
print("menu.json geschrieben.")
print("menu.txt geschrieben.")
