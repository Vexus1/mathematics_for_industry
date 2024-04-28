import os
import pandas as pd


# route_stations = [
#     "Katowice",
#     "Chorzów Batory",
#     "Zabrze",
#     "Gliwice",
#     "Lubliniec",
#     "Olesno Śląskie",
#     "Kluczbork",
#     "Byczyna Kluczborska",
#     "Kępno",
#     "Ostrzeszów",
#     "Ostrów Wielkopolski",
#     "Pleszew",
#     "Jarocin",
#     "Środa Wielkopolska",
#     "Poznań Główny"
# ]
# travel_times_minutes = [5, 10, 8, 39, 20, 15, 13, 17, 14, 18, 18, 14, 20, 23, 0]
os.chdir(os.path.dirname(os.path.abspath(__file__)))

route_stations = pd.read_csv('wroclaw_warsaw.csv')
route_stations = route_stations['Station Name'].to_list()[::-1]
travel_times_minutes = pd.read_csv('wroclaw_warsaw.csv')['Travel Time'].astype(int).to_list()[::-1]
travel_times_minutes[:-1] = travel_times_minutes[1:]
travel_times_minutes[-1] = 0
header = "Station Name,Travel Time\n"
with open('warsaw_wroclaw.csv', 'w', encoding='utf-8-sig') as file:
    file.write(header)
    for station, travel_time in zip(route_stations, travel_times_minutes): 
        file.write(f"{station},{travel_time}\n")
