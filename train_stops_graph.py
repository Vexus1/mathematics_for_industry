import os

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from icecream import ic
from scipy.interpolate import interp1d

os.chdir(os.path.dirname(os.path.abspath(__file__)))

node_color = 'skyblue'  # Kolor węzłów
edge_color = 'lightgrey'  # Kolor krawędzi
train_color = 'red'  # Kolor pociągu
route_color = 'green'  # Kolor trasy

df_trips = pd.read_csv('inputs/trips.txt')  
df_stop_times = pd.read_csv('inputs/stop_times.txt')
df_stops = pd.read_csv('inputs/stops.txt')
df_transfers = pd.read_csv('inputs/transfers.txt')

unique_stops = df_stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']]
df_stop_times_sorted = df_stop_times.sort_values(by=['trip_id', 'stop_sequence'])
ic(type(unique_stops))
ic(type(df_stop_times_sorted))
df_edges = df_stop_times_sorted[['trip_id', 'stop_id']].assign(
    next_stop_id=df_stop_times_sorted.groupby('trip_id')
    ['stop_id'].shift(-1)
).dropna()

edges = list(zip(df_edges['stop_id'], df_edges['next_stop_id'].astype(np.int64)))
G = nx.Graph()
for _, row in unique_stops.iterrows():
    G.add_node(row['stop_id'], pos=(row['stop_lon'], row['stop_lat']), label=row['stop_name'])

for edge in edges:
    if edge[0] in G.nodes and edge[1] in G.nodes:
        G.add_edge(edge[0], edge[1])

route_stations = pd.read_csv('traces/wroclaw_warsaw.csv')
route_stations = route_stations['Station Name'].tolist()
route_id = []
for station in route_stations:
    route_id.append(unique_stops[unique_stops['stop_name'] == station]['stop_id'].values[0])

pos = {node: (data['pos'][0], data['pos'][1]) for node, data in G.nodes(data=True)}
# ic(len(pos.keys()))
fig, ax = plt.subplots(figsize=(10, 8))
travel_times_minutes = [18, 7, 20, 30, 21, 5, 24, 26, 23, 18, 10, 19, 5]
total_travel_time = sum(travel_times_minutes)
time_points = np.cumsum([0] + travel_times_minutes)
distance_points = np.arange(len(route_id))
time_to_distance_interp = interp1d(time_points, distance_points, bounds_error=False, fill_value="extrapolate")
def update_route_with_interpolation_and_path(frame_number, total_frames, G, pos, route_id, route_stations, total_travel_time):
    ax.clear()
    # Rysowanie całej sieci kolejowej z mniejszą intensywnością
    nx.draw(G, pos, ax=ax, node_size=20, alpha=0.3, node_color="blue", edge_color="gray")

    # Interpolacja pozycji pociągu na trasie
    current_time = (frame_number / total_frames) * total_travel_time
    current_position = time_to_distance_interp(current_time)
    current_station_index = int(np.floor(current_position))
    if current_station_index + 1 < len(route_id):
        next_station_index = current_station_index + 1
    else: 
        current_station_index
    
    # Rysowanie trasy jako zielonej linii, która rozwija się wraz z pociągiem
    if next_station_index < len(route_id):
        current_station_pos = pos[route_id[current_station_index]]
        next_station_pos = pos[route_id[next_station_index]]
        interp_ratio = current_position - current_station_index
        interp_pos = (1 - interp_ratio) * np.array(current_station_pos) + interp_ratio * np.array(next_station_pos)
        ax.plot(*interp_pos, 'ro', markersize=12)  # Pociąg jako czerwony punkt

    # Rysowanie trasy jako zielonej linii, która rozwija się wraz z pociągiem
    route_path = route_id[:next_station_index + 1]
    route_edges = list(zip(route_path[:-1], route_path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color="green", width=2)

    # Etykieta dla aktualnej stacji
    labels = {route_id[current_station_index]: route_stations[current_station_index]}
    nx.draw_networkx_labels(G, pos, labels=labels, font_color="black")
    
    ax.set_title(f"Animacja podróży pociągu: {route_stations[0]} -> {route_stations[-1]}")
    plt.axis('off')

# Utworzenie i uruchomienie animacji
total_frames = 1000
interval_ms = (total_travel_time / total_frames) * 1000  
ani_route_with_interpolation_and_path = FuncAnimation(fig, update_route_with_interpolation_and_path, 
                                                      frames=total_frames, 
                                                      fargs=(total_frames, G, pos, route_id, route_stations, total_travel_time),
                                                      interval=interval_ms, repeat=False)

# plt.show()
ani_route_with_interpolation_and_path.save('outputs/train_journey_real_route_animation_interpolated.gif', writer='imagemagick', fps=30)