import os

import pandas as pd
from icecream import ic
from pandas import DataFrame

from matplotlib.animation import FuncAnimation
from interpolation_func import InterpolationFunc
from station_graph import StationGraph

def load_data() -> tuple[DataFrame, DataFrame, list[DataFrame]]:
    """
    Loads data from CSV files regarding stops, stop times, and traces.
    Returns:
        tuple: Returns a tuple containing a DataFrame for stops,
               a DataFrame for stop times, and a list of DataFrames for traces.
    """
    stops = pd.read_csv('inputs/stops0.txt')
    stop_times = pd.read_csv('inputs/stop_times0.txt')
    traces = [pd.read_csv('traces/CH.csv'),
              #pd.read_csv('traces/katowice_poznan.csv')]
              pd.read_csv('traces/AF.csv'),
              pd.read_csv('traces/BG.csv')]
    return stops, stop_times, traces

def save_anim(animation: FuncAnimation) -> None:
    """
    Saves the animation to a GIF file.
    Args:
        animation (FuncAnimation): The animation to be saved.
    Notes:
        The animation is saved using ImageMagick with the frame rate set to 30 FPS.
    """
    animation.save('outputs/train_anim.gif', writer='imagemagick', fps=30)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    stops, stop_times, traces = load_data()
    station_grap = StationGraph(stops, stop_times, traces)
    train_simulation = InterpolationFunc(station_grap)
    save_anim(train_simulation)
