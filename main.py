import os
from dataclasses import dataclass, field

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from icecream import ic
from pandas import DataFrame
from scipy.interpolate import interp1d
from matplotlib.animation import FuncAnimation
from typing import Any

from constants import *

@dataclass
class TrainSimulation:
    stops: DataFrame 
    stop_times: DataFrame 
    trips: DataFrame 
    trace: DataFrame
    G: nx.Graph = field(default_factory=nx.Graph)
    node_pos: dict = field(init=False)

    def __post_init__(self) -> None:
        # self.G = nx.Graph()
        self.create_nodes()
        self.node_pos = self.node_postion()
        self.route_stations = self.trace_names()
        self.route_id = self.train_path()

    def transform_data(self) -> tuple[DataFrame, DataFrame]:
        stops = self.stops[['stop_id', 'stop_name',
                            'stop_lat', 'stop_lon']]
        stop_times = self.stop_times.sort_values(
            by=['trip_id', 'stop_sequence'])
        return stops, stop_times

    def create_nodes(self) -> None:
        stops, stop_times = self.transform_data()
        next_stop_id = stop_times.groupby('trip_id')['stop_id'].shift(-1)
        df_edges = stop_times[['trip_id', 'stop_id']].assign(
                               next_stop_id=next_stop_id).dropna()
        edges = zip(df_edges['stop_id'],
                    df_edges['next_stop_id'].astype(np.int64))
        edges = list(edges)
        for _, row in stops.iterrows():
            self.G.add_node(row['stop_id'], pos=(row['stop_lon'],
                            row['stop_lat']), label=row['stop_name'])
        for edge in edges:
            if edge[0] in self.G.nodes and edge[1] in self.G.nodes:
                self.G.add_edge(edge[0], edge[1])
    
    def trace_names(self) -> list[str]:
        return self.trace['Station Name'].tolist()
    
    def train_path(self) -> list[np.int64]:
        route_id = []
        for station in self.route_stations:
            temp = self.stops[self.stops['stop_name'] == station]['stop_id'].values[0]
            route_id.append(temp)
        return route_id

    def node_postion(self) -> dict[any, tuple]:
        position = {node: (data['pos'][0], data['pos'][1])
                    for node, data in self.G.nodes(data=True)}
        return position
    
    def travel_time(self) -> list[int]:
        return self.trace['Travel Time'].astype(int)
    
    def travel_time_sum(self) -> int:
        return sum(self.travel_time())

    def total_travel_time(self) -> interp1d:
        time_points = np.cumsum([0] + self.travel_time())
        distance_points = np.arange(len(self.route_id))
        time_to_distance = interp1d(time_points, distance_points,
                                    bounds_error=False,
                                    fill_value="extrapolate")
        return time_to_distance

    def create_graph(self) -> tuple[plt.Figure, Any]:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.clear()
        nx.draw(self.G, self.node_pos, ax=ax, node_size=20,
                alpha=0.3, node_color="blue", edge_color=EDGE_COLOR)
        return fig, ax
    
    def update_graph(self, next_station_index: int) -> None:
        route_path = self.route_id [:next_station_index + 1]
        route_edges = list(zip(route_path[:-1], route_path[1:]))
        nx.draw_networkx_edges(self.G, self.node_pos, 
                               edgelist=route_edges,
                               edge_color=TRAVEL_COLOR, width=2)

    def stations_title(self, ax: Any, curr_station_index: int) -> None:
        label_key = self.route_id[curr_station_index]
        label_value = self.route_stations[curr_station_index]
        labels = {label_key: label_value}
        nx.draw_networkx_labels(self.G, self.node_pos,
                                labels=labels, font_color=FONT_COLOR)
        ax.set_title(f"Animacja podróży pociągu: {self.route_stations[0]} -> {self.route_stations[-1]}")
        plt.axis('off')

    def interp_func(self, frame_number: int, ax: Any) -> None:
        current_time = (frame_number / FRAMES) * self.travel_time_sum()
        current_position = self.total_travel_time()(current_time)
        current_station_index = int(np.floor(current_position))
        if current_station_index + 1 < len(self.route_id):
            next_station_index = current_station_index + 1
        else: 
            current_station_index = len(self.route_id) - 1  # Aby uniknąć indeksowania poza zakresem
            next_station_index = current_station_index
        current_station_pos = self.node_pos[self.route_id[current_station_index]]
        next_station_pos = self.node_pos[self.route_id[next_station_index]]
        interp_ratio = current_position - current_station_index
        interp_pos = (1 - interp_ratio) * np.array(current_station_pos) + interp_ratio * np.array(next_station_pos)
        ax.plot(*interp_pos, 'ro', markersize=12)  # Rysuj pociąg
        self.update_graph(next_station_index)
        self.stations_title(ax, current_station_index)

    def create_anim(self) -> FuncAnimation:
        fig, ax = self.create_graph()
        interval_ms = (self.travel_time_sum() / FRAMES) * 1000
        animation = FuncAnimation(fig, self.interp_func, fargs=(ax,),
                                frames=FRAMES, interval=interval_ms, repeat=False)
        return animation

def load_data() -> tuple[DataFrame, DataFrame, DataFrame, DataFrame]:
    stops = pd.read_csv('inputs/stops.txt')
    stop_times = pd.read_csv('inputs/stop_times.txt')
    trips = pd.read_csv('inputs/trips.txt')
    trace = pd.read_csv('traces/wroclaw_warsaw.csv')
    return stops, stop_times, trips, trace

def save_anim(animation: FuncAnimation) -> None:
    animation.save('outputs/train_anim.gif', writer='imagemagick', fps=30)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    train_simulation = TrainSimulation(*load_data())
    save_anim(train_simulation.create_anim())
