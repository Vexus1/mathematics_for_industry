from station_graph import *
from constants import TRAVEL_COLOR

class InterpolationFunc(StationGraph):
    def __post_init__(self):
        # super().__init__(self.G, self.node_pos, self.fig,
        #                   self.ax, self.routes_id)
        pass

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
    
