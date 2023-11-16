import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from typing import List, Tuple
import pandas as pd
from matplotlib.patches import Polygon
from typing import Dict
import tkinter.ttk as ttk
import json
import math
from .DraggablePoint import DraggablePoint
from Helpers.helpers import add_website_link, set_plot_color, _from_rgb, round_point_00_2
from .SpotifyPlayer import SpotifyPlayer
from .Monitor import Monitor
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Credentials.Credentials import Credentials
from Configs.Parser import Parser
import matplotlib.animation as animation
import multiprocessing
import time
import random
import sched, time
from .TableDropDown import TableDropDown
from .Radar import Radar

try:
    from ..Database import Database
    from ..Client import APIClient
except ImportError:
    import sys
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))

    from Database import Database
    from Client import APIClient

class Spotify():
    """
    Class to handle the middle frame of the GUI where the music is handled
    """

    def __init__(self):
        """
        Initialize the Radar class with Spotify credentials as well as database
        """
        self.__db_cr = Credentials.get_database_credentials()
        self.__db_id = self.__db_cr['id']
        self.__db_password = self.__db_cr['password']
        self.__db_name = self.__db_cr["db_name"]
        self.__spotify_cr = Credentials.get_spotify_credentials()
        if len(self.__spotify_cr['username']) == 0 or \
            len(self.__spotify_cr['client_id']) == 0 or \
                len(self.__spotify_cr['client_secret']) == 0:
                    print("Warning, Spotify credentials not found, will skip it")
        self.client = APIClient([self.__spotify_cr['username']],
                                [self.__spotify_cr['client_id']],
                                [self.__spotify_cr['client_secret']])

        self.data_to_save = {}

        # TODO: maybe currently playing later
        self.currently_playing = self.client.get_current_track()

    def build_frame(self, window: ttk.Frame, bg_string:str, fg_string:str):
        """
        Build the frame of the GUI for the Radar plot

        :param window: the Frame of the Window
        :type window: ttk.Frame
        :param bg_string: the background color
        :type bg_string: str
        :param fg_string: the foreground color
        :type fg_string: str
        """
        self.window = window
        self.move_flag = False
        self.area = None
        self.bg_string = bg_string
        self.fg_string = fg_string
        self.color_theme = Parser.get_plt_theme()
        self.color_palette = plt.get_cmap(self.color_theme)(np.linspace(0, 1, 7))[1:-1]

        # add spotify website link on to spotify
        text = "Spotify"
        url = "https://open.spotify.com/?"
        font= ('Aerial', '16', 'underline')
        side = "top"
        add_website_link(self.window, url, text, font, side,
                         fg = self.fg_string, bg = self.bg_string)

        self.radar = Radar(self.window, self.__db_id, self.__db_password,
                           self.__db_name, self.fg_string, self.bg_string,
                           self.currently_playing, self.color_palette, self.client)
        # Initialize the spotify player to play songs
        spotify_player_frame = ttk.Frame(self.window)
        spotify_player_frame.pack(side='bottom', anchor='c', fill='both', expand=True)
        self.spotify_player = SpotifyPlayer(spotify_player_frame,
                                            self.update_monitor,
                                            self.__spotify_cr,
                                            self.fg_string,
                                            self.bg_string)
        self.radar.plot_radar()

    # def update_radar(self):
    #     """
    #     Update the radar plot
    #     """
    #     self.radar.update_radar()

    def update_monitor(self, action: str):
        """
        Update the monitor based on the action that was performed on SpotifyPlayer

        :param action: the action name
        :type action: str
        """
        if action == "pause":
            # remove the plot
            self.radar.playing[0].remove()
        else:
            self.radar.change_song()
