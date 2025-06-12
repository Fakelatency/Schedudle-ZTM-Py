import requests
import json

RESOURCE_ID = "ab75c33d-3a26-4342-b36a-6e5fef0a3ac3"
API_KEY = os.getenv("API_KEY")
URL = "https://api.um.warszawa.pl/api/action/dbstore_get"

print("Pobieram słowniczek przystanków z API ZTM...")

try:
    response = requests.get(URL, params={"id": RESOURCE_ID, "apikey": API_KEY})
    response.raise_for_status()

    data = response.json()

    parsed_stops = []
    for entry in data['result']:
        values = {item['key']: item['value'] for item in entry['values']}
        stop_info = {
            'id': values.get('zespol'),
            'number': values.get('slupek'),
            'name': values.get('nazwa_zespolu'),
            'direction': values.get('kierunek')
        }
        parsed_stops.append(stop_info)

    with open('przystanki.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_stops, f, ensure_ascii=False, indent=4)

    print(f"✅ Pomyślnie zapisano {len(parsed_stops)} przystanków do pliku 'przystanki.json'.")

except requests.exceptions.RequestException as e:
    print(f"❌ Wystąpił błąd podczas komunikacji z API: {e}")
except KeyError:
    print("❌ Otrzymano nieprawidłowy format danych z API.")