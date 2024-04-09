import os

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML

os.chdir(os.path.dirname(os.path.abspath(__file__)))

df_trips = pd.read_csv('inputs/trips.txt')
df_stop_times = pd.read_csv('inputs/stop_times.txt')
df_stops = pd.read_csv('inputs/stops.txt')
df_transfers = pd.read_csv('inputs/transfers.txt')

unique_stops = df_stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].drop_duplicates()
stop_id_to_name = unique_stops.set_index('stop_id')['stop_name'].to_dict()
df_stop_times_sorted = df_stop_times.sort_values(by=['trip_id', 'stop_sequence'])
df_edges = df_stop_times_sorted[['trip_id', 'stop_id']].assign(
    next_stop_id=df_stop_times_sorted.groupby('trip_id')['stop_id'].shift(-1)
).dropna()

edges = list(zip(df_edges['stop_id'], df_edges['next_stop_id'].astype(np.int64)))

G = nx.Graph()
for index, row in unique_stops.iterrows():
    G.add_node(row['stop_id'], pos=(row['stop_lon'], row['stop_lat']), label=row['stop_name'])

for edge in edges:
    if edge[0] in G.nodes and edge[1] in G.nodes:
        G.add_edge(edge[0], edge[1])

start_station = unique_stops[unique_stops['stop_name'] == "Wrocław Główny"]['stop_id'].values[0]
end_station = unique_stops[unique_stops['stop_name'] == "Warszawa Centralna"]['stop_id'].values[0]
path = nx.shortest_path(G, source=start_station, target=end_station)
pos = {node: (data['pos'][0], data['pos'][1]) for node, data in G.nodes(data=True)}


plt.close()
fig, ax = plt.subplots(figsize=(10, 8))

def update(num, G, pos, path, path_edges):
    ax.clear()
    nx.draw(G, pos, ax=ax, node_size=20, alpha=0.3, node_color="blue", edge_color="gray")
    nx.draw_networkx_nodes(G, pos, nodelist=path[:num+1], node_size=50, node_color="red")
    nx.draw_networkx_edges(G, pos, edgelist=path_edges[:num], width=2, edge_color="red")
    labels = {start_station: 'Wrocław Główny', end_station: 'Warszawa Centralna'}
    if num < len(path):
        labels[path[num]] = G.nodes[path[num]]['label']
    nx.draw_networkx_labels(G, pos, labels=labels, font_color="green")
    ax.set_title("Animacja podróży pociągu: Wrocław Główny -> Warszawa Centralna")
    plt.axis('off')

path_edges = list(zip(path, path[1:]))  #
ani = FuncAnimation(fig, update, frames=len(path) + 5, fargs=(G, pos, path, path_edges), interval=1000, repeat=False)
ani.save('outputs/train_journey_animation.gif', writer='imagemagick', fps=1)
