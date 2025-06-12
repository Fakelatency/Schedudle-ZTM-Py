import json
import time
from datetime import timedelta
import warsaw_data_api

PLIK_PRZYSTANKI = 'przystanki.json'
PLIK_WYJSCIOWY = 'baza_linii.json'
API_KEY = os.getenv("API_KEY")

print("Rozpoczynam proces indeksowania linii dla wszystkich przystanków.")
print(f"Dane wejściowe: {PLIK_PRZYSTANKI}")
print("UWAGA: Ten proces może potrwać ponad godzinę!")

try:
    with open(PLIK_PRZYSTANKI, 'r', encoding='utf-8') as f:
        all_stops = json.load(f)
except FileNotFoundError:
    print(f"❌ Błąd: Nie znaleziono pliku '{PLIK_PRZYSTANKI}'.")
    print("   Upewnij się, że najpierw uruchomiłeś skrypt 'pobierz_przystanki.py'.")
    exit()

ztm = warsaw_data_api.ztm(apikey=API_KEY)
line_to_stops_map = {}
total_stops = len(all_stops)
start_time = time.time()

for i, stop in enumerate(all_stops):
    if (i + 1) % 10 == 0:
        elapsed_time = time.time() - start_time
        avg_time_per_stop = elapsed_time / (i + 1)
        remaining_stops = total_stops - (i + 1)
        estimated_remaining_time = timedelta(seconds=int(remaining_stops * avg_time_per_stop))
        print(f"Przetwarzam przystanek {i + 1}/{total_stops}... Szacowany pozostały czas: {estimated_remaining_time}")

    try:
        lines_on_stop = ztm.get_lines_for_bus_stop_id(stop['id'], stop['number'])

        time.sleep(0.1)

        if not lines_on_stop:
            continue

        for line in lines_on_stop:
            if line is None:
                continue

            if line not in line_to_stops_map:
                line_to_stops_map[line] = []

            line_to_stops_map[line].append(stop)

    except Exception as e:
        print(f"⚠️ Wystąpił błąd przy przystanku {stop['id']}-{stop['number']}: {e}. Kontynuuję.")
        continue

print("\n✅ Zakończono indeksowanie.")
print(f"Znaleziono {len(line_to_stops_map)} unikalnych linii.")
print(f"Zapisuję dane do pliku {PLIK_WYJSCIOWY}...")

with open(PLIK_WYJSCIOWY, 'w', encoding='utf-8') as f:
    json.dump(line_to_stops_map, f, ensure_ascii=False, indent=4)

print("✅ Baza danych linii została pomyślnie utworzona!")