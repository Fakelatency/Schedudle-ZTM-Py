import os
import json
from datetime import datetime
import requests

# --- Konfiguracja i funkcje pomocnicze ---

API_KEY = os.getenv("API_KEY")
BAZA_LINII = 'baza_linii.json'

def wczytaj_baze_linii(plik=BAZA_LINII):
    """Wczytuje kompletną bazę linii i przystanków z pliku JSON."""
    try:
        with open(plik, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Błąd: Nie znaleziono pliku bazy '{plik}'.")
        print("   Upewnij się, że najpierw uruchomiłeś skrypt 'indeksuj_linie.py'.")
        return None

def pobierz_rozkład_bezposrednio(bus_stop_id, bus_stop_nr, line):
    """Pobiera rozkład bezpośrednio z API ZTM."""
    URL = "https://api.um.warszawa.pl/api/action/dbtimetable_get"
    params = {
        "id": "e923fa0e-d96c-43f9-ae6e-60518c9f3238",
        "busstopId": bus_stop_id, "busstopNr": bus_stop_nr,
        "line": line, "apikey": API_KEY,
    }
    response = requests.get(URL, params=params)
    response.raise_for_status()
    data = response.json()

    if not data.get('result') or not isinstance(data['result'], list):
        return []

    odjazdy = []
    for odjazd_jako_lista in data['result']:
        wartosci = {item['key']: item['value'] for item in odjazd_jako_lista}
        if 'czas' in wartosci:
            odjazdy.append(wartosci['czas'])
    return odjazdy



def main():
    line_database = wczytaj_baze_linii()
    if line_database is None:
        return

    print("✅ Baza danych wczytana.")
    all_lines = sorted(line_database.keys())
    print("\n🚍 Dostępne linie komunikacji miejskiej:")

    print(", ".join(all_lines))
    
    chosen_line = input("\nWybierz numer linii: ").upper()
    if chosen_line not in line_database:
        print("❌ Nie znaleziono takiej linii w bazie.")
        return


    stops_for_line = line_database[chosen_line]
    directions = sorted(list(set(stop['direction'] for stop in stops_for_line if stop['direction'])))
    
    print("\n➡️ Dostępne kierunki dla linii " + chosen_line + ":")
    for i, direction in enumerate(directions):
        print(f"{i + 1}. {direction}")

    try:
        dir_choice_idx = int(input("Wybierz kierunek: ")) - 1
        chosen_direction = directions[dir_choice_idx]
    except (ValueError, IndexError):
        print("❌ Nieprawidłowy wybór.")
        return


    route_stops = [stop for stop in stops_for_line if stop['direction'] == chosen_direction]
    unique_route_stops = list({f"{stop['id']}-{stop['number']}": stop for stop in route_stops}.values())

    print(f"\n📍 Trasa w kierunku '{chosen_direction}':")
    for i, stop in enumerate(unique_route_stops):
        print(f"{i + 1}. {stop['name']} {stop['number']}")

    try:
        stop_choice_idx = int(input("Wybierz przystanek z trasy: ")) - 1
        selected_stop = unique_route_stops[stop_choice_idx]
    except (ValueError, IndexError):
        print("❌ Nieprawidłowy wybór.")
        return

    try:
        print(f"\nPobieram rozkład dla linii {chosen_line} z przystanku {selected_stop['name']} {selected_stop['number']}...")
        all_today_departures = pobierz_rozkład_bezposrednio(selected_stop['id'], selected_stop['number'], chosen_line)
        
        if all_today_departures:
            current_date_str = datetime.now().strftime('%A, %d.%m.%Y')
            print(f"\n✅ Odjazdy na dziś ({current_date_str}):")
            
            now = datetime.now().time()
            future_departures = []
            for t in all_today_departures:
                if t.startswith('24:'):
                    future_departures.append(t)
                else:
                    if datetime.strptime(t, '%H:%M:%S').time() >= now:
                        future_departures.append(t)

            if future_departures:
                for i in range(0, len(sorted(future_departures)), 6):
                    print("   ".join(sorted(future_departures)[i:i+6]))
            else:
                print("Brak dalszych odjazdów w dniu dzisiejszym.")
        else:
            print("Brak odjazdów dla tej linii na tym przystanku w dniu dzisiejszym.")
            
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd przy pobieraniu rozkładu: {e}")

if __name__ == "__main__":
    main()