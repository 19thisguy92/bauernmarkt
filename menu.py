import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

URL = "http://www.bauernmarkt-wels.at/"

# --------------------------------------------------------
# Zeitzone
# --------------------------------------------------------

TZ = ZoneInfo("Europe/Vienna")
NOW = datetime.now(TZ)

print("Systemzeit:", NOW.strftime("%d.%m.%Y %H:%M:%S"))

# --------------------------------------------------------
# Homepage laden
# --------------------------------------------------------

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
# Menübereich finden
# --------------------------------------------------------

marker = "gabis_menue_logo.png"

pos = html.find(marker)

if pos == -1:
    raise Exception("Menülogo nicht gefunden!")

bereich = html[pos:pos + 8000]

print("Menübereich gefunden.")

# --------------------------------------------------------
# Datum auslesen
# --------------------------------------------------------

datum_match = re.search(
    r"Freitag,\s*([0-9]{1,2})\.\s*([A-Za-zÄÖÜäöü]+)\s*([0-9]{4})",
    bereich
)

if not datum_match:
    raise Exception("Datum nicht gefunden!")

tag = int(datum_match.group(1))
monat_name = datum_match.group(2)
jahr = int(datum_match.group(3))

MONATE = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12
}

if monat_name not in MONATE:
    raise Exception(f"Unbekannter Monat: {monat_name}")

monat = MONATE[monat_name]

menu_datum = datetime(jahr, monat, tag, tzinfo=TZ)

datum_text = f"Freitag, {tag}. {monat_name} {jahr}"

print("Datum:", datum_text)

# --------------------------------------------------------
# Aktuell?
# --------------------------------------------------------

current = (
    NOW.date() == menu_datum.date()
)

print("Aktuell:", current)

# --------------------------------------------------------
# Menü auslesen
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
# JSON schreiben
# --------------------------------------------------------

daten = {
    "restaurant": "Bauernmarkt Wels",
    "url": URL,
    "updated": NOW.isoformat(),
    "menu_date": datum_text,
    "current": current,
    "menu": menue
}

with open("menu.json", "w", encoding="utf-8") as f:
    json.dump(
        daten,
        f,
        ensure_ascii=False,
        indent=4
    )

# --------------------------------------------------------
# TXT schreiben
# --------------------------------------------------------

with open("menu.txt", "w", encoding="utf-8") as f:

    f.write("Bauernmarkt Wels\n")
    f.write("================\n\n")

    f.write(datum_text + "\n")

    if current:
        f.write("(Aktuelles Menü)\n\n")
    else:
        f.write("(Menü ist NICHT aktuell)\n\n")

    for eintrag in menue:
        f.write(f"• {eintrag}\n")

print()
print("menu.json geschrieben.")
print("menu.txt geschrieben.")
