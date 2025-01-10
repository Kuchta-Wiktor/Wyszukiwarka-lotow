import sqlite3
import random
from datetime import datetime, timedelta

airports = [
    "WAW", "JFK", "LHR", "ORD", "CDG", "AMS", "DXB", "MAD", "SYD", "FCO", "BKK", "YVR", "YYZ", "IST", "ICN", "NRT",
    "SFO", "KUL", "TLV", "PEK", "SEA", "CGK", "DEL", "SAN", "CPT",
    "HNL", "SVO", "STL", "LIM", "CLT", "MIA", "PHX", "ATL", "SLC",
    "YUL", "MXP", "WUH", "AKL", "DTW", "BCN", "DUB", "GIG", "CUN",
    "TPE", "VIE", "KTM", "ZRH", "MLE", "LHE", "JNB", "LED", "BCN",
    "BOM", "RIX", "BNE", "ATH", "DME", "KIX", "SHA", "YOW", "GRU",
    "SCL", "MAN", "SIN", "CGH", "NCE", "TUL", "LCA", "BUD", "OPO",
    "LIN", "KMG", "EZE", "CMB", "MEL", "KRK", "GDN", "FCO", "LAX", "POZ"
]

airlines_hubs = {
    "Lufthansa": ["MUC"],
    "Emirates": ["DXB"],
    "Qatar Airways": ["DOH"],
    "Iberia": ["MAD"],
    "SAS": ["CPH", "ARN"],
    "British Airways": ["LHR", "LGW"],
    "American Airlines": ["DFW", "JFK"],
    "Copa": ["PTY"],
    "LATAM": ["GRU", "SCL"],
    "Turkish Airlines": ["IST"],
    "Austrian": ["VIE"],
    "KLM": ["AMS"],
    "Air France": ["CDG"],
    "Ethiopian": ["ADD"],
    "Caribbean Airlines": ["POS"],
    "LOT": ["WAW"],
    "Finnair": ["HEL"],
    "Condor": ["FRA"],
    "TAP": ["LIS"],
    "Brussels": ["BRU"],
    "Swiss": ["ZRH"],
    "Aegean": ["ATH"],
    "Volotea": ["VCE"],
    "Air Serbia": ["BEG"],
    "Smartwings": ["PRG"],
    "Etihad": ["AUH"],
    "Royal Jordanian": ["AMM"],
    "Kuwait Airways": ["KWI"],
    "Bangkok Airways": ["BKK"],
    "Royal Brunei": ["BWN"],
    "Air Astana": ["ALA"],
    "Qantas": ["SYD"],
    "Jetstar": ["SYD"],
    "Air New Zealand": ["AKL"],
    "Copa": ["PTY"],
    "Air Canada": ["YYZ"],
    "United": ["ORD"],
    "Porter Airlines": ["YYZ"],
    "WestJet": ["YYC"],
    "Spirit": ["MIA"],
    "JetBlue": ["JFK"],
    "Avianca": ["BOG"],
    "LATAM": ["SCL"],
    "Aerolinas Argentinas": ["EZE"],
    "Gol Brazil": ["GRU"],
    "Azul Linhas Aereas Brasileiras": ["VCP"],
    "South African Airways": ["JNB"]
}


connection = sqlite3.connect("flights.db")

cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airline TEXT NOT NULL,
        flight_number TEXT NOT NULL,
        departure_airport TEXT NOT NULL,
        arrival_airport TEXT NOT NULL,
        departure_day INTEGER NOT NULL,
        departure_time TEXT NOT NULL,
        valid_from DATE,
        valid_until DATE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS airline_hubs (
        airline TEXT PRIMARY KEY,
        hub1 TEXT,
        hub2 TEXT
    )
''')

for airline, hubs in airlines_hubs.items():
    cursor.execute('''
        INSERT OR REPLACE INTO airline_hubs (airline, hub1, hub2) 
        VALUES (?, ?, ?)
    ''', (airline, hubs[0], hubs[1] if len(hubs) > 1 else None))

def random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

def random_day():
    return random.randint(1, 7)

def random_dates():
    start_date = datetime.today() + timedelta(days=random.randint(0, 30))  # Losowy start od dzisiaj
    end_date = start_date + timedelta(days=random.randint(90, 180))  # Losowy start od dzisiaj
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

# Dodawanie 100 rekordów dla każdej linii lotniczej, uwzględniając huby
for airline in airlines_hubs:
    hubs = airlines_hubs[airline]

    for _ in range(500):
        # Wybór jednego z hubów danej linii lotniczej
        departure_airport = random.choice(hubs)
        arrival_airport = random.choice([airport for airport in airports if airport != departure_airport])

        departure_day = random_day()
        departure_time = random_time()
        valid_from, valid_until = random_dates()

        # Tworzenie numeru rejsu - nieparzysty numer dla wylotu, parzysty dla powrotu
        flight_number_out = f"{airline[:2].upper()}{random.randint(101, 4999) * 2 - 1}"  # Nieparzysty
        flight_number_return = f"{airline[:2].upper()}{random.randint(101, 4999) * 2}"  # Parzysty (powrotny)

        # Wstawienie lotu wylotowego
        cursor.execute('''
            INSERT INTO flights (
                airline, flight_number, departure_airport, arrival_airport, 
                departure_day, departure_time,
                valid_from, valid_until
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            airline, flight_number_out, departure_airport, arrival_airport,
            departure_day, departure_time,
            valid_from, valid_until
        ))

        # Dodawanie lotu powrotnego z numerem rejsu parzystym
        cursor.execute('''
            INSERT INTO flights (
                airline, flight_number, departure_airport, arrival_airport, 
                departure_day, departure_time, 
                valid_from, valid_until
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            airline, flight_number_return, arrival_airport, departure_airport,
            departure_day, departure_time,
            valid_from, valid_until
        ))

# Zatwierdzanie zmian w bazie danych
connection.commit()

# Pobieranie danych w celu sprawdzenia
cursor.execute('SELECT * FROM flights LIMIT 10')
for row in cursor.fetchall():
    print(row)

# Zamykanie połączenia z bazą danych
connection.close()
