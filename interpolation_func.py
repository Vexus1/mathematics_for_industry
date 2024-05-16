from dataclasses import dataclass
from typing import Any

import numpy as np
import networkx as nx
from scipy.interpolate import interp1d
from matplotlib.animation import FuncAnimation
from matplotlib.pyplot import Axes

from station_graph import StationGraph # warning: circular import 
from constants import *

@dataclass
class InterpolationFunc():
    graph: StationGraph

    def __post_init__(self):
        self.routes_id = self.graph.routes_id
        self.node_pos = self.graph.node_pos
        pass

    def interp_travels_times(self) -> list[interp1d]:
        """
        Generates interpolating functions mapping cumulative travel times
        to distances for each route.
        Returns:
            list: A list of interpolating functions from cumulative time points 
            to distances.
        """
        total = []
        for i in range(len(self.graph.traces)):
            time_points = np.cumsum([0] + self.graph.travels_times()[i])
            distance_points = np.arange(len(self.routes_id[i]))
            time_to_distance = interp1d(time_points, distance_points,
                                        bounds_error=False,
                                        fill_value="extrapolate")
            total.append(time_to_distance)
        return total

    def update_draw(self, ax: Axes) -> None:
        ax.clear()
        nx.draw(self.graph.G, self.node_pos, ax=ax, node_size=20,
                alpha=0.3, node_color=NODE_COLOR, edge_color=EDGE_COLOR)
        
    def current_time(self) -> int:
        pass

    def update_time(self) -> None:
        pass

    def update_position(self) -> None:
        pass

    def update_graph(self) -> None:
        pass

    def train_arrived(self) -> bool:
        pass
    
    def draw_trains(self) -> None:
        pass

    def node_locked(self) -> bool:
        pass

    def main_func(self) -> None:
        pass
    
    def create_anim(self) -> FuncAnimation:
        pass
