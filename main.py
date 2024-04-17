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
from constants import *

@dataclass
class TrainSimulation:
    stops: DataFrame 
    stop_times: DataFrame 
    trips: DataFrame 
    trace: DataFrame

    def __post_init__(self) -> None:
        self.G: nx.Graph = nx.Graph()

    def transform_data(self) -> tuple[DataFrame, DataFrame]:
        stops = self.stops[['stop_id', 'stop_name',
                            'stop_lat', 'stop_lon']]
        stop_times = self.stop_times.sort_values(
            by=['trip_id', 'stop_sequence'])
        return stops, stop_times

    def create_nodes(self) -> None:
        stops, stop_times = self.transform_data()
        df_edges = stop_times[['trip_id', 'stop_id']].assign(
            next_stop_id = stop_times.groupby('trip_id')
            ['stop_id'].shift(-1)
        ).dropna()
        edges = list(zip(df_edges['stop_id'],
                         df_edges['next_stop_id'].astype(np.int64)))
        for _, row in stops.iterrows():
            self.G.add_node(row['stop_id'], pos=(row['stop_lon'],
                            row['stop_lat']), label=row['stop_name'])
        for edge in edges:
            if edge[0] in self.G.nodes and edge[1] in self.G.nodes:
                self.G.add_edge(edge[0], edge[1])
    
    def train_path(self) -> list[np.int64]:
        route_stations = self.trace['Station Name'].tolist()
        route_id = []
        for station in route_stations:
            temp = self.stops[self.stops['stop_name'] == station]
            ['stop_id'].values[0]
            route_id.append(temp)
        return route_id

    def node_postion(self) -> dict[any, tuple]:
        position = {node: (data['pos'][0], data['pos'][1])
               for node, data in self.G.nodes(data=True)}
        return position

    def travel_time(self) -> interp1d:
        time = self.trace['Travel Time']
        time_points = np.cumsum([0] + time)
        distance_points = np.arange(len(self.train_path()))
        time_to_distance = interp1d(time_points, distance_points,
                                    bounds_error=False,
                                    fill_value="extrapolate")
        return time_to_distance

    def create_graph(self):
        pass

    def interpolation_function(self):
        pass

    def update(self):
        pass


def load_data() -> tuple[DataFrame, DataFrame, DataFrame]:
    stops = pd.read_csv('inputs/stops.txt')
    stop_times = pd.read_csv('inputs/stop_times.txt')
    trips = pd.read_csv('inputs/trips.txt')
    trace = pd.read_csv('traces/wroclaw_warsaw')
    return stops, stop_times, trips, trace

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ic(TrainSimulation(*load_data()).stops)
