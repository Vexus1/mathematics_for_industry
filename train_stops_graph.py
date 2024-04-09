import os

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))

df_trips = pd.read_csv('inputs/trips.txt')
df_stop_times = pd.read_csv('inputs/stop_times.txt')
df_stops = pd.read_csv('inputs/stops.txt')
unique_stops = df_stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].drop_duplicates()
stop_id_to_name = unique_stops.set_index('stop_id')['stop_name'].to_dict()
unique_stops.head(), stop_id_to_name[list(stop_id_to_name.keys())[0]]
df_stop_times_sorted = df_stop_times.sort_values(by=['trip_id', 'stop_sequence'])
df_edges = df_stop_times_sorted[['trip_id', 'stop_id']].assign(next_stop_id=df_stop_times_sorted.groupby('trip_id')['stop_id'].shift(-1)).dropna()
edges = list(zip(df_edges['stop_id'], df_edges['next_stop_id'].astype(np.int64)))
G = nx.Graph()
for index, row in unique_stops.iterrows():
    G.add_node(row['stop_id'], pos=(row['stop_lon'], row['stop_lat']), label=row['stop_name'])

for edge in edges:
    if edge[0] in G.nodes and edge[1] in G.nodes:
        G.add_edge(edge[0], edge[1])

plt.figure(figsize=(15, 10))
pos = {node:(data['pos'][0], data['pos'][1]) for node, data in G.nodes(data=True)}
nx.draw(G, pos, node_size=50, node_color="blue", alpha=0.6, with_labels=False)
nx.draw_networkx_labels(G, pos, {node:data['label'] for node, data in G.nodes(data=True) if data['label'] in ["Wrocław Główny", "Warszawa Centralna"]}, font_color="red")
plt.title("Mapa grafowa stacji kolejowych w Polsce")
plt.xlabel("Długość geograficzna")
plt.ylabel("Szerokość geograficzna")
plt.show()
