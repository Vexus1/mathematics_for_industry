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

header = "Station Name\n"
with open('wroclaw_warsaw.csv', 'w', encoding='utf-8-sig') as file:
    file.write(header)
    for station in route_stations:
        file.write(f"{station}\n")
