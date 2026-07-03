import requests

url = "http://www.bauernmarkt-wels.at/"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

print("Status:", response.status_code)

with open("homepage.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTML gespeichert.")
