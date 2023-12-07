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
from Drive.Drive import Drive
import subprocess
from Database.Database import Database
import datetime

try:
    # from ..Database import Database
    from ..Client import APIClient
except ImportError:
    import sys
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))

    # from Database import Database
    from Client import APIClient

class Spotify():
    """
    Class to handle the middle frame of the GUI where the music is handled
    """

    def __init__(self, db):
        """
        Initialize the Radar class with Spotify credentials as well as database
        """
        # self.__db_cr = Credentials.get_database_credentials()
        # self.__db_id = self.__db_cr['id']
        # self.__db_password = self.__db_cr['password']
        self.db = db
        self.__spotify_cr = Credentials.get_spotify_credentials()
        if len(self.__spotify_cr['username']) == 0 or \
            len(self.__spotify_cr['client_id']) == 0 or \
                len(self.__spotify_cr['client_secret']) == 0:
                    print("Warning, Spotify credentials not found, will skip it")
        self.client = APIClient([self.__spotify_cr['username']],
                                [self.__spotify_cr['client_id']],
                                [self.__spotify_cr['client_secret']])
        self.device_id = Parser.get_device_id()
        self.data_to_save = {
            'ts': [],
            'id': [],
            'reason_start': [],
            'reason_end': [],
            'paused': []
        }
        # try:
        #     self.db = Database(self.__db_id, self.__db_password)
        # except TimeoutError:
        #     self.db = Drive()
        # from AppData\Local\Packages\SpotifyAB.SpotifyMusic_zpdnekdrzrea0
        # subprocess.Popen(["spotify.exe"])

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
        link_frame = ttk.Frame(self.window)
        link_frame.pack(side='top', anchor='c', fill='both', expand=True)
        text = "Spotify"
        url = "https://open.spotify.com/?"
        font= ('Aerial', '16', 'underline')
        side = "left"
        add_website_link(link_frame, url, text, font, side,
                         fg = self.fg_string, bg = self.bg_string)

        self.radar = Radar(self.window, self.db, self.fg_string, self.bg_string,
                           self.color_palette, self.client, self.change_playlist)
        # Initialize the spotify player to play songs
        spotify_player_frame = ttk.Frame(self.window)
        spotify_player_frame.pack(side='bottom', anchor='c', fill='both', expand=True)
        self.spotify_player = SpotifyPlayer(spotify_player_frame,
                                            self.update_monitor,
                                            self.db,
                                            self.__spotify_cr,
                                            self.fg_string,
                                            self.bg_string)
        # currently playing is empty when Spotify is closed or just opened but
        # nothing has been played yet. Otherwise we have the is_playing = True/False
        self.currently_playing = self.client.get_current_track(self.device_id)
        if self.currently_playing:
            name = self.currently_playing['item']['name']
        else:
            name = "None"
        self.text_var = tk.StringVar()
        self.text_var.set(f'Playing: {name}')
        self.song_name_label = ttk.Label(link_frame, textvariable=self.text_var, font=("Arial",16))
        self.song_name_label.pack(side = tk.LEFT, anchor = 'c',fill='both', expand=True)
        self.radar.prepare_plot(self.text_var)
        if self.currently_playing:
            if self.currently_playing['is_playing'] == True:
                self.data_to_save['ts'].append(datetime.datetime.now())
                self.data_to_save['id'].append(self.currently_playing['item']['id'])
                self.data_to_save['reason_start'].append("open")
                self.start_thread()
                self.spotify_player.set_playing(True)
            else:
                self.spotify_player.set_playing(False)

        self.radar.plot_radar(self.currently_playing)

    def change_playlist(self):
        """
        Plays a new playlist from the Radar plot
        """
        self.data_to_save['reason_end'].append('playlist')
        self.data_to_save['reason_start'].append("playlist")
        try:
            self.data_to_save['paused'].append(time.time() - self.start_pause)
            self.start_pause = None
        except (AttributeError, TypeError):
            self.data_to_save['paused'].append(0)
        self.change_song()

    def start_thread(self):
        self.event = threading.Event()
        self.submit_thread = threading.Thread(target=self.show_song,
                                                args=(self.event,))
        self.submit_thread.daemon = True
        self.submit_thread.start()

    def show_song(self, event: tk.Event):
        """
        Show a song features values on the plot

        :param event: _description_
        :type event: tk.Event
        """
        time_rest = round((self.currently_playing['item']['duration_ms']-\
            self.currently_playing['progress_ms'])/1000)
        self.monitor = Monitor(time_rest, self.change_song)
        self.monitor.schedule.run()

    def change_song(self, schedule: sched=None):
        """
        Update the Monitor with the song that is now playing

        :param schedule: needed when callback, defaults to None
        :type schedule: sched, optional
        """
        print(schedule)
        if schedule:
            # it finished the song naturally (no button pressed) or a new playlist
            # has been runned
            self.data_to_save['reason_end'].append('trackdone')
            self.data_to_save['reason_start'].append("trackdone")
            try:
                self.data_to_save['paused'].append(datetime.datetime.now() - self.start_pause)
                self.start_pause = None
            except (AttributeError, TypeError):
                self.data_to_save['paused'].append(0)
        time.sleep(2)
        self.currently_playing = self.client.get_current_track(self.device_id)
        self.data_to_save['ts'].append(datetime.datetime.now())
        # Watch out it has time to update the currently_playing
        try:
            self.data_to_save['id'].append(self.currently_playing['item']['id'])
            time_rest = round(self.currently_playing['item']['duration_ms']/1000)
        except TypeError:
            return
        try:
            self.monitor.new_song(time_rest)
        except (AttributeError, TypeError):
            self.monitor = Monitor(time_rest, self.change_song)
            self.monitor.new_song(time_rest)
        self.radar.update_currently_playing(self.currently_playing)
        self.radar.update_plot()
        print(self.data_to_save)

    def update_monitor(self, action: str):
        """
        Update the monitor based on the action that was performed on SpotifyPlayer

        :param action: the action name
        :type action: str
        """
        if action == "like":
            print(self.currently_playing)
            return self.currently_playing
        if action == "play":
            if len(self.data_to_save['ts']) == 0:
                time.sleep(2)
                self.currently_playing = self.client.get_current_track(self.device_id)
                # we haven't played anything yet, this is the first song
                self.data_to_save['ts'].append(datetime.datetime.now())
                self.data_to_save['id'].append(self.currently_playing['item']['id'])
                self.data_to_save['reason_start'].append("open")
                self.start_thread()
                self.radar.update_currently_playing(self.currently_playing)
                self.radar.update_plot()
            else:
                # we just resumed the song
                self.radar.update_plot()
                try:
                    if len(self.data_to_save['paused'])<len(self.data_to_save['ts']):
                        self.data_to_save['paused'].append(datetime.datetime.now() - self.start_pause)
                        self.start_pause = None
                    else:
                        self.data_to_save['paused'][-1] += datetime.datetime.now() - self.start_pause
                        self.start_pause = None
                except (AttributeError, TypeError):
                    # the song was not playing before
                    pass
        elif action == "pause":
            self.start_pause = datetime.datetime.now()
        elif action == "next":
            self.change_song()
            # Watch out it has time to update the currently_playing
            self.data_to_save['reason_start'].append("next")
            self.data_to_save['reason_end'].append('next')
            try:
                self.data_to_save['paused'].append(datetime.datetime.now() - self.start_pause)
                self.start_pause = None
            except (AttributeError, TypeError):
                self.data_to_save['paused'].append(0)
        elif action == "previous":
            self.change_song()
            self.data_to_save['ts'].append(datetime.datetime.now())
            # Watch out it has time to update the currently_playing
            # TODO: maybe knows
            self.data_to_save['reason_start'].append("previous")
            self.data_to_save['reason_end'].append('previous')
            try:
                self.data_to_save['paused'].append(datetime.datetime.now() - self.start_pause)
                self.start_pause = None
            except (AttributeError, TypeError):
                self.data_to_save['paused'].append(0)
        print(self.data_to_save)

    def save_data(self):
        """
        Saves data into Raspberry Pi
        """
        self.radar.save_data()
        self.spotify_player.save_data()
        if len(self.data_to_save['reason_end'])<len(self.data_to_save['ts']):
            self.data_to_save['reason_end'].append('close')
        if len(self.data_to_save['paused'])<len(self.data_to_save['ts']):
            try:
                self.data_to_save['paused'].append(datetime.datetime.now() - self.start_pause)
                self.start_pause = None
            except (AttributeError, TypeError):
                self.data_to_save['paused'].append(0)
        self.save_data_to_save()

    def save_data_to_save(self):
        """
        Save the data to save into the the Raspberry
        """
        self.db.save_history_data(self.data_to_save)
