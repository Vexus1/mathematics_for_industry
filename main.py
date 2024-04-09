import os
from dataclasses import dataclass

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from icecream import ic

@dataclass
class TrainSimulation:
    stops: pd.DataFrame = None
    stop_times: pd.DataFrame = None
    trips: pd.DataFrame = None

    def __post_init__(self):
        self.stops = pd.read_csv('inputs/stops.txt')
        self.stop_times = pd.read_csv('inputs/stop_times.txt')
        self.trips = pd.read_csv('inputs/trips.txt')
   
# df = pd.read_csv(f"inputs/routes.txt")
# print(df.head())


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
