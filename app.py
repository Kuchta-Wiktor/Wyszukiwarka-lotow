import math
import sqlite3
from datetime import datetime, timedelta

import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Weryfikacja hasła dla admina
ADMIN_PASSWORD = 'qwerty'
admin_authenticated = False


# Funkcja do łączenia się z bazą danych
def get_db_connection():
    conn = sqlite3.connect('flights.db')
    conn.row_factory = sqlite3.Row
    return conn


# Funkcja do pobierania współrzędnych lotniska z opencage API
def get_airport_coordinates(airport_code):
    api_key = '65df2352f66e45fa8abd147a2cc10850'  # Wstaw tutaj swój klucz API
    url = f'https://api.opencagedata.com/geocode/v1/json?q={airport_code}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lng = data['results'][0]['geometry']['lng']
        return lat, lng
    else:
        return None, None  # Jeśli nie znaleziono współrzędnych


# Funkcja do obliczania odległości między dwoma punktami na podstawie współrzędnych geograficznych (wzór Haversine)
def haversine(lat1, lon1, lat2, lon2):
    r = 6371  # Promień Ziemi w kilometrach
    d_lat = math.radians(lat2 - lat1)
    d_lot = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(d_lot / 2) * math.sin(d_lot / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = r * c  # Odległość w kilometrach
    return distance


# Funkcja do obliczania czasu lotu w godzinach
def calculate_flight_duration(departure_airport, arrival_airport):
    dep_lat, dep_lon = get_airport_coordinates(departure_airport)
    arr_lat, arr_lon = get_airport_coordinates(arrival_airport)

    if dep_lat is None or arr_lat is None:
        return None  # Jeśli nie udało się pobrać współrzędnych

    distance = haversine(dep_lat, dep_lon, arr_lat, arr_lon)
    average_speed = 800  # Średnia prędkość samolotu w km/h
    flight_duration_hours = distance / average_speed + 0.5  # Czas lotu w godzinach + 30 min buforu na start i lądowanie

    # Zamiana na format GG:MM
    hours = int(flight_duration_hours)
    minutes = int((flight_duration_hours - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"


# Funkcja wyszukująca dostępne połączenia
def search_flights(departure_airport, arrival_airport, date_str):
    # Obliczanie dnia tygodnia (1 - poniedziałek, 7 - niedziela)
    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
    day_of_week = date_obj.weekday() + 1  # weekday() zwraca 0 dla poniedziałku, więc dodajemy 1
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    lookup_date = f"{year}-{month:02d}-{day:02d}"  # Formatowanie, aby zawsze mieć dwucyfrowy miesiąc i dzień

    connection = get_db_connection()
    cursor = connection.cursor()

    # Wyszukiwanie lotów pasujących do dnia tygodnia i kodów lotnisk
    cursor.execute('''
        SELECT airline, flight_number, departure_airport, arrival_airport, departure_day,
                departure_time, valid_from, valid_until
        FROM flights
        WHERE departure_airport = ? AND arrival_airport = ? AND departure_day = ? 
        AND date(?) BETWEEN date(valid_from) AND date(valid_until)
    ''', (departure_airport.upper(), arrival_airport.upper(), day_of_week, lookup_date))

    flights = cursor.fetchall()

    flight_details = []

    if not flights:
        flight_details.append(f"No flights available from {departure_airport} to {arrival_airport} on {date_str}.")
    else:
        for flight in flights:
            airline, flight_number, dep_airport, arr_airport, dep_day, dep_time, valid_from, valid_until = flight
            flight_duration = calculate_flight_duration(dep_airport, arr_airport)

            if flight_duration is not None:
                arrival_time = datetime.strptime(dep_time, "%H:%M") + timedelta(hours=int(flight_duration[:2]),
                                                                                minutes=int(flight_duration[3:]))

                flight_details.append({
                    "airline": airline,
                    "flight_number": flight_number,
                    "departure_airport": dep_airport,
                    "arrival_airport": arr_airport,
                    "departure_time": dep_time,
                    "arrival_time": arrival_time.strftime('%H:%M'),
                    "flight_duration": flight_duration,
                    "valid_from": valid_from,
                    "valid_until": valid_until
                })
            else:
                flight_details.append(f"Could not calculate flight duration for {flight_number}.")

    connection.close()

    return flight_details


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search_flights')
def search_flights_page():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    departure_airport = request.form['departure_airport']
    arrival_airport = request.form['arrival_airport']
    date_str = request.form['date']

    flights = search_flights(departure_airport, arrival_airport, date_str)
    """print(f"Flights data: {flights}")"""
    return render_template('results.html', flights=flights)


# Strona admina (z weryfikacją hasła)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global admin_authenticated
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            admin_authenticated = True
            return redirect('/admin')
        else:
            return render_template('admin.html', error="Nieprawidłowe hasło", admin_authenticated=False)
    return render_template('admin.html', admin_authenticated=admin_authenticated)


# Dodawanie nowego lotu
@app.route('/admin/add_flight', methods=['POST'])
def add_flight():
    if not admin_authenticated:
        return redirect('/admin')

    airline = request.form['airline']
    flight_number = request.form['flight_number']
    departure_airport = request.form['departure_airport']
    arrival_airport = request.form['arrival_airport']
    departure_day = int(request.form['departure_day'])
    departure_time = request.form['departure_time']
    valid_from = request.form['valid_from']
    valid_until = request.form['valid_until']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO flights (airline, flight_number, departure_airport, arrival_airport,
                            departure_day, departure_time, valid_from, valid_until)
        VALUES (?, ?, ?, ?, ?, ?,?,?)
    ''', (
        airline, flight_number, departure_airport, arrival_airport, departure_day, departure_time, valid_from,
        valid_until))
    conn.commit()
    conn.close()

    return redirect('/admin')


# Usuwanie lotu
@app.route('/admin/remove_flight', methods=['POST'])
def remove_flight():
    if not admin_authenticated:
        return redirect('/admin')

    flight_number = request.form['flight_number']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM flights WHERE flight_number = ?', (flight_number,))
    conn.commit()
    conn.close()

    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)
