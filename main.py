import os
import json
from datetime import datetime
import requests
import warsaw_data_api

API_KEY = os.getenv("API_KEY")

def wczytaj_przystanki_z_pliku(plik='przystanki.json'):
    try:
        with open(plik, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Błąd: Nie znaleziono pliku '{plik}'.")
        print("   Upewnij się, że najpierw uruchomiłeś skrypt do pobirania przystanków.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Błąd: Plik '{plik}' jest uszkodzony lub ma nieprawidłowy format.")
        return None


def pobierz_rozkład_bezposrednio(bus_stop_id, bus_stop_nr, line):

    SCHEDULE_RESOURCE_ID = "e923fa0e-d96c-43f9-ae6e-60518c9f3238"
    URL = "https://api.um.warszawa.pl/api/action/dbtimetable_get"

    params = {
        "id": SCHEDULE_RESOURCE_ID,
        "busstopId": bus_stop_id,
        "busstopNr": bus_stop_nr,
        "line": line,
        "apikey": API_KEY,
    }

    response = requests.get(URL, params=params)
    response.raise_for_status()
    data = response.json()

    if not data.get('result') or not isinstance(data['result'], list):
        return []

    odjazdy = []
    for odjazd_jako_lista in data['result']:
        wartosci_odjazdu = {item['key']: item['value'] for item in odjazd_jako_lista}
        if 'czas' in wartosci_odjazdu:
            odjazdy.append(wartosci_odjazdu['czas'])

    return odjazdy


def main():
    all_stops = wczytaj_przystanki_z_pliku()
    if all_stops is None:
        return

    print(f"✅ Pomyślnie wczytano {len(all_stops)} przystanków z lokalnej bazy.")

    stop_query = input("\n🔎 Podaj nazwę szukanego przystanku (np. CENTRUM): ").upper()
    matching_stops = [s for s in all_stops if stop_query in s['name'].upper()]

    if not matching_stops:
        print(f"Nie znaleziono przystanków pasujących do '{stop_query}'.")
        return

    unique_stops_dict = {f"{s['id']}-{s['number']}": s for s in matching_stops}
    unique_stops = list(unique_stops_dict.values())

    print("\n📍 Wybierz konkretny przystanek (słupek):")
    for i, stop in enumerate(unique_stops):
        print(f"{i + 1}. {stop['name']} {stop['number']} (kierunek: {stop['direction']})")

    try:
        choice_idx = int(input(f"Wybierz numer porządkowy (1-{len(unique_stops)}): ")) - 1
        selected_stop = unique_stops[choice_idx]
    except (ValueError, IndexError):
        print("❌ Nieprawidłowy wybór.")
        return

    try:
        ztm = warsaw_data_api.ztm(apikey=API_KEY)
        lines_on_stop = ztm.get_lines_for_bus_stop_id(selected_stop['id'], selected_stop['number'])
        lines_on_stop = sorted([line for line in lines_on_stop if line])
        if not lines_on_stop:
            print("Na tym przystanku nie znaleziono żadnych linii.")
            return

        print("\n✅ Na tym przystanku dostępne są linie:")
        for i, line in enumerate(lines_on_stop):
            print(f"{i + 1}. {line}")

        prompt = f"Wybierz numer porządkowy z listy (1-{len(lines_on_stop)}): "
        choice_idx_line = int(input(prompt)) - 1
        chosen_line = lines_on_stop[choice_idx_line]

    except (ValueError, IndexError):
        print("❌ Nieprawidłowy wybór linii.")
        return
    except Exception as e:
        print(f"Wystąpił błąd przy pobieraniu listy linii: {e}")
        return

    try:
        print(
            f"\nPobieram rozkład dla linii {chosen_line} z przystanku {selected_stop['name']} {selected_stop['number']}...")
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
                # Domyślne sortowanie alfabetyczne zadziała tu poprawnie ("23:59" < "24:05")
                for i in range(0, len(sorted(future_departures)), 6):
                    print("   ".join(sorted(future_departures)[i:i + 6]))
            else:
                print("Brak dalszych odjazdów w dniu dzisiejszym.")
        else:
            print("Brak odjazdów dla tej linii na tym przystanku w dniu dzisiejszym.")

    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd przy pobieraniu rozkładu: {e}")


if __name__ == "__main__":
    main()