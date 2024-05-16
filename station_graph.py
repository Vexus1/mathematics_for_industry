from dataclasses import dataclass

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pandas import DataFrame
from icecream import ic
from typing import Any
from matplotlib.pyplot import Figure
from matplotlib.pyplot import Axes

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
        """
        Transforms the data about stops and stop times into required formats.
        """
        stops = self.stops[['stop_id', 'stop_name',
                            'stop_lat', 'stop_lon']]
        stop_times = self.stop_times.sort_values(
            by=['trip_id', 'stop_sequence'])
        return stops, stop_times
    
    def create_nodes(self) -> None:
        """
        Creates nodes and edges in the graph based on the processed data.
        """
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
        """
        Determines the positions of nodes in the graph.
        Returns:
            dict: A dictionary of node positions.
        """
        position = {node: (data['pos'][0], data['pos'][1])
                    for node, data in self.G.nodes(data=True)}
        return position
    
    def create_graph(self) -> tuple[Figure, Axes]:
        """
        Creates a visualization of the graph.
        Returns:
            tuple: Returns a matplotlib figure and 
            axis object representing the graph.
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.clear()
        nx.draw(self.G, self.node_pos, ax=ax, node_size=20,
                alpha=0.3, node_color=NODE_COLOR, edge_color=EDGE_COLOR)
        return fig, ax

    def train_paths(self) -> list[list[np.int64]]:
        """
        Computes the IDs of the stations for each route.
        Returns:
            list: A list of lists containing station IDs
            for each route based on station names.
        """
        routes_id = []
        for route in self.route_stations:
            route_id = []
            for station in route:
                temp = self.stops[self.stops['stop_name'] == station]['stop_id'].values[0]
                route_id.append(temp)
            routes_id.append(route_id)
        return routes_id
    
    def travels_times(self) -> list[list[int]]:
        """
        Extracts the travel times for each route from the trace data.
        Returns:
            list: A list of travel times lists, extracted from the trace data.
        """
        times = []
        for trace in self.traces:
            real_time = trace[trace['Travel Time'] != 0]
            real_time = real_time['Travel Time'].astype(int).tolist() 
            times.append(real_time)
        return times
    
    def travels_times_sum(self) -> list[int]:
        """
        Calculates the sum of travel times for each route.
        Returns:
            list: A list of summed travel times for each route.
        """
        return [sum(travel) for travel in self.travels_times()]

    def trace_names(self) -> list[list[str]]:
        return [trace['Station Name'].tolist() for trace in self.traces]
