# Aplikacja do zarządzania lotami

Aplikacja umożliwia użytkownikom wyszukiwanie i zarządzanie lotami między różnymi lotniskami, a także oferuje interfejs administratora do dodawania i usuwania lotów.

## Technologie

- **SQLite3**: Używana do przechowywania informacji o lotach i hubach linii lotniczych w bazie danych.
- **Flask**: Framework webowy wykorzystywany do budowy aplikacji i zarządzania trasami.
- **Requests**: Biblioteka umożliwiająca wykonywanie zapytań do API w celu pozyskiwania współrzędnych geograficznych lotnisk.
- **HTML/CSS**: Używane do tworzenia frontendowych stron aplikacji.

## Funkcje

### 1. System zarządzania lotami
- **Wyszukiwanie lotów**: Umożliwia wyszukiwanie dostępnych lotów poprzez wybór lotniska początkowego, docelowego oraz daty.
- **Szczegóły lotów**: Wyświetla informacje o locie, takie jak linia lotnicza, numer lotu, godzina wylotu/przylotu, czas lotu.
- **Panel administratora**: Użytkownicy z uprawnieniami administracyjnymi mogą zalogować się do panelu i zarządzać lotami, dodając lub usuwając wpisy lotów.

### 2. Obliczanie lotów
- **Obliczanie odległości**: Aplikacja wykorzystuje wzór Haversine do obliczania odległości między dwoma lotniskami na podstawie ich współrzędnych geograficznych.
- **Obliczanie czasu lotu**: Aplikacja szacuje czas lotu na podstawie odległości i średniej prędkości samolotu (800 km/h).

## Struktura bazy danych

1. **flights**: Przechowuje informacje o lotach, w tym:
   - **airline**: Linia lotnicza wykonująca lot.
   - **flight_number**: Unikalny numer lotu.
   - **departure_airport**: Lotnisko wylotu.
   - **arrival_airport**: Lotnisko przylotu.
   - **departure_day**: Dzień tygodnia, w którym lot odbywa się.
   - **departure_time**: Godzina wylotu.
   - **valid_from**: Data początkowa ważności lotu.
   - **valid_until**: Data końcowa ważności lotu.

2. **airline_hubs**: Przechowuje informacje o hubach linii lotniczych oraz powiązanych z nimi lotniskach.

## Podstawowe trasy

- **Strona główna** `/`: Strona startowa aplikacji.
- **Wyszukiwanie lotów** `/search_flights`: Formularz do wyszukiwania lotów.
- **Strona wyników** `/search`: Wyświetla wyniki wyszukiwania lotów.
- **Panel administratora** `/admin`: Strona logowania do panelu administratora.
- **Dodawanie nowego lotu** `/admin/add_flight`: Dodawanie nowego lotu (tylko dla administratora).
- **Usuwanie lotu** `/admin/remove_flight`: Usuwanie istniejącego lotu (tylko dla administratora).

## Użytkowanie

### Wyszukiwanie lotów:
1. Wybierz lotnisko początkowe, docelowe oraz datę, aby znaleźć dostępne loty.

### Panel administratora:
1. Aby uzyskać dostęp do panelu administratora, należy zalogować się za pomocą hasła.
2. Domyślne hasło to `qwerty`.
3. Po zalogowaniu można dodać nowe loty lub usunąć istniejące.
