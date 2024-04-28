import os
from dataclasses import dataclass

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from icecream import ic
from pandas import DataFrame
from scipy.interpolate import interp1d
from matplotlib.animation import FuncAnimation
from typing import Any
from collections import defaultdict

from constants import *

@dataclass
class TrainSimulation:
    stops: DataFrame 
    stop_times: DataFrame 
    traces: list[DataFrame]

    def __post_init__(self) -> None:
        self.G = nx.Graph()
        self.create_nodes()
        self.routes_stations = self.traces_names()
        self.routes_id = self.trains_paths()
        self.node_pos = self.node_postion()
        self.fig, self.ax = self.create_graph()
        self.station_occupancy = defaultdict(lambda: None)  
        self.total_frames = [FRAMES * (self.travels_times_sum()[i] / max(self.travels_times_sum())) for i, _ in enumerate(self.traces)]
        self.total_paused_time = [0] * len(self.traces)  
        self.paused_time = {i: 0 for i in range(len(self.traces))}  
        self.paused_positions = {i: None for i in range(len(self.traces))}  

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
    
    def traces_names(self) -> list[list[str]]:
        return [trace['Station Name'].tolist() for trace in self.traces]
    
    def trains_paths(self) -> list[list[np.int64]]:
        routes_id = []
        for route in self.routes_stations:
            route_id = []
            for station in route:
                temp = self.stops[self.stops['stop_name'] == station]['stop_id'].values[0]
                route_id.append(temp)
            routes_id.append(route_id)
        return routes_id

    def node_postion(self) -> dict[any, tuple]:
        position = {node: (data['pos'][0], data['pos'][1])
                    for node, data in self.G.nodes(data=True)}
        return position
    
    def travels_times(self) -> list[list[int]]:
        times = []
        for trace in self.traces:
            real_time = trace[trace['Travel Time'] != 0]
            real_time = real_time['Travel Time'].astype(int).tolist() 
            times.append(real_time)
        return times
    
    def travels_times_sum(self) -> list[int]:
        return [sum(travel) for travel in self.travels_times()]

    def total_travels_times(self) -> list[interp1d]:
        total = []
        for i in range(len(self.traces)):
            time_points = np.cumsum([0] + self.travels_times()[i])
            distance_points = np.arange(len(self.routes_id[i]))
            time_to_distance = interp1d(time_points, distance_points,
                                        bounds_error=False,
                                        fill_value="extrapolate")
            total.append(time_to_distance)
        return total

    def create_graph(self) -> tuple[plt.Figure, Any]:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.clear()
        nx.draw(self.G, self.node_pos, ax=ax, node_size=20,
                alpha=0.3, node_color=NODE_COLOR, edge_color=EDGE_COLOR)
        return fig, ax
    
    def update_graph(self, next_station_index: int, route_id: list) -> None:
        route_path = route_id[:next_station_index + 1]
        route_edges = list(zip(route_path[:-1], route_path[1:]))
        nx.draw_networkx_edges(self.G, self.node_pos,
                            edgelist=route_edges,
                            edge_color=TRAVEL_COLOR, width=2)

    def interp_func(self, frame_number, ax):
        ax.clear()
        nx.draw(self.G, self.node_pos, ax=ax, node_size=20,
                alpha=0.3, node_color=NODE_COLOR, edge_color=EDGE_COLOR)
        for i in range(len(self.traces)):
            adjusted_total_time = self.travels_times_sum()[i] + self.paused_time[i]
            adjusted_total_frames = FRAMES * (adjusted_total_time / max(self.travels_times_sum()[j]
                                                                         + self.paused_time[j] for j in range(len(self.traces))))
            if frame_number <= adjusted_total_frames:
                current_time = (frame_number / adjusted_total_frames) * adjusted_total_time - self.paused_time[i]
                current_position = self.total_travels_times()[i](current_time)
            else:
                current_position = len(self.routes_id[i]) - 1 

            current_station_index = int(np.floor(current_position))
            current_station_index = min(current_station_index, len(self.routes_id[i]) - 1)
            if current_station_index + 1 < len(self.routes_id[i]):
                next_station_index = current_station_index + 1
            else:
                next_station_index = current_station_index
            current_station_pos = self.node_pos[self.routes_id[i][current_station_index]]
            if next_station_index < len(self.routes_id[i]):
                current_train_at_station = self.station_occupancy[self.routes_id[i][next_station_index]]
                if current_train_at_station is not None and current_train_at_station != i:
                    if self.paused_positions[i] is None:  
                        interp_ratio = current_position - current_station_index
                        self.paused_positions[i] = (1 - interp_ratio) * np.array(current_station_pos)
                        + interp_ratio * np.array(self.node_pos[self.routes_id[i][next_station_index]])
                    ax.plot(*self.paused_positions[i], 'ro', markersize=12)
                    self.paused_time[i] += 1 / adjusted_total_frames * adjusted_total_time  
                    continue

            self.paused_positions[i] = None 
            if next_station_index < len(self.routes_id[i]):
                next_station_pos = self.node_pos[self.routes_id[i][next_station_index]]
                interp_ratio = current_position - current_station_index
                interp_pos = (1 - interp_ratio) * np.array(current_station_pos) + interp_ratio * np.array(next_station_pos)
                ax.plot(*interp_pos, 'ro', markersize=12)
            else:
                ax.plot(*current_station_pos, 'ro', markersize=12)

            self.update_graph(next_station_index, self.routes_id[i])
            if current_station_index > 0 and next_station_index != current_station_index:
                self.station_occupancy[self.routes_id[i][current_station_index - 1]] = None
            self.station_occupancy[self.routes_id[i][current_station_index]] = i

    def create_anim(self) -> FuncAnimation:
        max_total_time = max(self.travels_times_sum()[i] + self.total_paused_time[i] for i in range(len(self.traces)))
        interval_ms = (max_total_time / max(self.total_frames)) * 1000
        animation = FuncAnimation(self.fig, self.interp_func, fargs=(self.ax,),
                                frames=FRAMES, interval=interval_ms, repeat=False)
        return animation


def load_data() -> tuple[DataFrame, DataFrame, list[DataFrame]]:
    stops = pd.read_csv('inputs/stops.txt')
    stop_times = pd.read_csv('inputs/stop_times.txt')
    traces = [pd.read_csv('traces/wroclaw_warsaw.csv'),
              pd.read_csv('traces/katowice_poznan.csv')]
    return stops, stop_times, traces

def save_anim(animation: FuncAnimation) -> None:
    animation.save('outputs/train_anim.gif', writer='imagemagick', fps=30)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    train_simulation = TrainSimulation(*load_data())
    save_anim(train_simulation.create_anim())
