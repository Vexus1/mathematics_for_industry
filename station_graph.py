from dataclasses import dataclass

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pandas import DataFrame
from icecream import ic
from typing import Any
from matplotlib.pyplot import Figure
from scipy.interpolate import interp1d

from constants import NODE_COLOR, EDGE_COLOR

@dataclass
class StationGraph:
    stops: DataFrame
    stop_times: DataFrame
    traces: list[DataFrame]

    def __post_init__(self):
        self.G = nx.Graph()
        self.create_nodes()
        self.route_stations = self.trace_names()
        self.routes_id = self.train_paths()
        self.node_pos = self.node_position()
        self.fig, self.ax = self.create_graph()

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

    def node_position(self) -> dict[Any, tuple]:
        position = {node: (data['pos'][0], data['pos'][1])
                    for node, data in self.G.nodes(data=True)}
        return position
    
    def create_graph(self) -> tuple[Figure, Any]:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.clear()
        nx.draw(self.G, self.node_pos, ax=ax, node_size=20,
                alpha=0.3, node_color=NODE_COLOR, edge_color=EDGE_COLOR)
        return fig, ax

    def train_paths(self) -> list[list[np.int64]]:
        routes_id = []
        for route in self.route_stations:
            route_id = []
            for station in route:
                temp = self.stops[self.stops['stop_name'] == station]['stop_id'].values[0]
                route_id.append(temp)
            routes_id.append(route_id)
        return routes_id
    
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
    
    def trace_names(self) -> list[list[str]]:
        return [trace['Station Name'].tolist() for trace in self.traces]
