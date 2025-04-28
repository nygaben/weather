import requests
import csv
import datetime  # Eredeti 'from datetime import datetime' helyett
import pytz      # <- Hozzáadva az időzónák kezeléséhez

# 1. API elérés adatai
# FONTOS: Az API kulcsot ne tedd közzé nyilvánosan! Érdemes lehet környezeti változóból olvasni.
API_KEY = "78da4aaa0b85035615659610ffadd84d" # Ez a te kulcsod, vigyázz rá!
CITY = "Tiszaujvaros,HU"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Időzóna beállítása
HELYI_IDOZONA = pytz.timezone('Europe/Budapest') # <- Itt add meg a kívánt időzónát

# --- Függvény a logikának (opcionális, de struktúráltabb) ---
def fetch_and_save_weather():
    """Lekéri az időjárás adatokat és elmenti CSV-be helyi idővel."""
    print(f"Adatlekérés indítása UTC szerint: {datetime.datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 2. Időjárás adat lekérése
        response = requests.get(URL)
        response.raise_for_status() # Hibát dob, ha a státuszkód nem 2xx

        # Sikeres kérés, feldolgozás
        data = response.json()

        # Ellenőrizzük, hogy a várt kulcsok léteznek-e
        if "main" in data and "wind" in data and "weather" in data and data["weather"]:

            # 3. Fontos adatok kigyűjtése
            # Idő lekérése UTC-ben, majd konvertálás helyi időre
            utc_now = datetime.datetime.now(pytz.utc)
            helyi_ido = utc_now.astimezone(HELYI_IDOZONA)
            now_str = helyi_ido.strftime("%Y-%m-%d %H:%M:%S") # <- Formázott string a CSV-hez és kiíráshoz

            temperature = data["main"]["temp"]
            pressure = data["main"]["pressure"]
            humidity = data["main"]["humidity"]
            wind_speed_mps = data["wind"]["speed"]
            wind_speed_kmh = wind_speed_mps * 3.6
            # data.get() biztonságosabb, ha a 'deg' kulcs hiányozhatna
            wind_deg = data.get("wind", {}).get("deg", "N/A") # Ha nincs 'wind' vagy 'deg' kulcs
            weather_description = data["weather"][0]["description"]

            # 4. Eredmény kiírása terminálra (helyi idővel)
            print(f"Idő (helyi): {now_str}")
            print(f"Hőmérséklet: {temperature} °C")
            print(f"Légnyomás: {pressure} hPa")
            print(f"Páratartalom: {humidity} %")
            print(f"Szélerősség: {wind_speed_kmh:.1f} km/h")
            print(f"Szélirány: {wind_deg}°")
            print(f"Időjárás: {weather_description}")

            # 5. Adatok mentése CSV fájlba
            # Módosított fejléc, hogy jelezze a helyi időt
            header = ["timestamp_local", "temperature_C", "pressure_hPa", "humidity_percent", "wind_speed_kmh", "wind_direction_deg", "description"]
            # Helyi idő string használata
            row = [now_str, temperature, pressure, humidity, round(wind_speed_kmh, 1), wind_deg, weather_description]
            filepath = "weather_data.csv"

            file_exists = False
            try:
                # Megpróbáljuk olvasásra megnyitni, hogy lássuk létezik-e (gyorsabb mint a stat)
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Itt akár ellenőrizhetnénk a fejlécet is, de most elég a létezés
                    if f.readline(): # Olvasunk egy sort, ha van tartalom, létezik és nem üres
                         file_exists = True
            except FileNotFoundError:
                file_exists = False
            except Exception as e:
                 print(f"Hiba a fájl ellenőrzésekor: {e}") # Egyéb olvasási hibák
                 # Döntsük el, mi történjen ilyenkor, talán próbáljuk meg írni?

            # Írás hozzáfűző módban ('a')
            with open(filepath, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Csak akkor írjuk a fejlécet, ha a fájl korábban nem létezett (vagy üres volt)
                if not file_exists:
                    writer.writerow(header)
                writer.writerow(row)
            print(f"Adat sikeresen mentve, helyi idő: {now_str}")

        else:
            # A JSON válasz struktúrája nem megfelelő
            print("Hiba: A kapott API válasz nem tartalmazza a várt adatokat.")
            print("Kapott adat:")
            print(data)

    except requests.exceptions.HTTPError as e:
        # Kifejezetten HTTP hibák kezelése (pl. 401 Unauthorized, 404 Not Found)
        print(f"Hiba: Nem sikerült lekérni az adatokat az API-tól (HTTP Hiba).")
        print(f"Státuszkód: {response.status_code}")
        try:
            error_data = response.json()
            print("API Hibaüzenet:", error_data.get("message", "Nincs üzenet"))
        except requests.exceptions.JSONDecodeError:
            print("API Válasz (nem JSON):", response.text)
        print(f"Részletes hiba: {e}")
    except requests.exceptions.RequestException as e:
        # Egyéb hálózati/kérés hibák (pl. kapcsolat, timeout)
        print(f"Hiba: Hálózati vagy kérés hiba történt.")
        print(f"Hiba részletei: {e}")
    except KeyError as e:
        # Hibakezelés arra az esetre, ha a JSON struktúra mégis hibás
        print(f"Hiba: Hiányzó kulcs a JSON válaszban: {e}")
        try:
            print("Kapott adat (részlet):", data) # Írassuk ki a kapott adatot debug célból
        except NameError:
             print("Nem sikerült a JSON adatot beolvasni.")
    except Exception as e:
        # Minden egyéb váratlan hiba elkapása
        print(f"Váratlan általános hiba történt: {e}")


# --- Szkript Fő Futtatása ---
if __name__ == "__main__":
    # Ez a rész akkor fut le, ha a szkriptet közvetlenül indítják
    # Ha schedule könyvtárral vagy time.sleep-pel használnád, akkor a
    # fetch_and_save_weather() hívást kellene időzíteni.
    # PythonAnywhere Scheduled Task esetén ez a blokk lefut egyszer, amikor a task elindul.
    fetch_and_save_weather()