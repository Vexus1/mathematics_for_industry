import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

route_stations = [
    "Wrocław Główny",
    "Oława",
    "Brzeg",
    "Opole Główne",
    "Lubliniec",
    "Częstochowa Stradom",
    "Częstochowa",
    "Radomsko",
    "Piotrków Trybunalski",
    "Koluszki",
    "Skierniewice",
    "Żyrardów",
    "Warszawa Zachodnia",
    "Warszawa Centralna"
]
travel_times_minutes = [18, 7, 20, 30, 21, 5, 24, 26, 23, 18, 10, 19, 5, 0]
header = "Station Name,Travel Time\n"
with open('wroclaw_warsaw.csv', 'w', encoding='utf-8-sig') as file:
    file.write(header)
    for station, travel_time in zip(route_stations, travel_times_minutes): 
        file.write(f"{station},{travel_time}\n")
