import os

import pandas as pd
from icecream import ic

os.chdir(os.path.dirname(os.path.abspath(__file__)))
stops = pd.read_csv('inputs/stops.txt')
stop_times = pd.read_csv('inputs/stop_times.txt')
trips = pd.read_csv('inputs/trips.txt')
print(type(stops))
wroclaw_stops = stops[stops['stop_name'].str.contains("Wrocław Główny", case=False, na=False)]
warsaw_stops = stops[stops['stop_name'].str.contains("Warszawa Centralna", case=False, na=False)]
ic(wroclaw_stops)
ic(warsaw_stops)
