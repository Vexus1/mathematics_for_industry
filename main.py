import os
from dataclasses import dataclass

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from icecream import ic
from pandas import DataFrame

@dataclass
class TrainSimulation:
    stops: DataFrame 
    stop_times: DataFrame 
    trips: DataFrame 

    def transform_data(self):
        pass

    def create_edges(self):
        pass

    def create_graph(self):
        pass

    def main_train_path(self):
        pass

    def update(self):
        pass


def load_data() -> tuple[DataFrame, DataFrame, DataFrame]:
    stops = pd.read_csv('inputs/stops.txt')
    stop_times = pd.read_csv('inputs/stop_times.txt')
    trips = pd.read_csv('inputs/trips.txt')
    return stops, stop_times, trips

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ic(TrainSimulation(*load_data()).stops)
