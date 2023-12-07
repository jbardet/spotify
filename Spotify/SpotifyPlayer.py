import tkinter as tk
from tkinter import ttk
import spotipy
from tkinter import messagebox
from Credentials.Credentials import Credentials
from datetime import datetime
from Drive.Drive import Drive
from typing import Callable, Dict
from Configs.Parser import Parser
from Database.Database import Database

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

class SpotifyPlayer():
    """
    SpotifyPlayer widget to play songs, pause, ...
    """

    def __init__(self,
                 window: tk.Frame,
                 callback: Callable,
                 db,
                 spotify_cr: Dict[str, str],
                 fg_string: str,
                 bg_string: str):
        """
        Initialize the SpotifyPlayer widget

        :param window: the frame where to put the widget
        :type window: tk.Frame
        :param callback: what to do when a button is pressed
        :type callback: Callable
        :param spotify_cr: the credentials from spotify
        :type spotify_cr: Dict[str, str]
        :param fg_string: the style of the foreground
        :type fg_string: str
        :param bg_string: the style of the background
        :type bg_string: str
        """
        self.window = window
        self.callback = callback
        self.db = db
        self.__spotify_cr = spotify_cr
        self.fg_string = fg_string
        self.bg_string = bg_string
        self.client = APIClient([self.__spotify_cr['username']],
                                [self.__spotify_cr['client_id']],
                                [self.__spotify_cr['client_secret']])
        self.liked_songs = {'name': [], 'id': [], 'time': [], 'type': []}
        self.device_id = Parser.get_device_id()
        # self.track_name = self.currently_playing['item']['name']

        self.button_width = 6
        # we listen in shuffle mode:
        # try:
        #     self.client.shuffle()
        # except spotipy.exceptions.SpotifyException as e:
        #     # no active device found
        #     #TODO: put in shuffle mode when start a song
        #     print(e)

        unlike_btn = ttk.Button(self.window, text='-', width=self.button_width,
                                  command=self.unlike, style='my.TButton')
        unlike_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

        # shuffle_btn = ttk.Button(self.window, text='~', width=self.button_width,
        #                           command=self.shuffle, style='my.TButton')
        # shuffle_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

        previous_btn = ttk.Button(self.window, text=' << ', width=self.button_width,
                                  command=self.previous, style='my.TButton')
        previous_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

        play_btn = ttk.Button(self.window, text=' |> ', width=self.button_width,
                              command=self.play, style='my.TButton')
        play_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

        pause_btn = ttk.Button(self.window, text=' || ', width=self.button_width,
                               command=self.pause, style='my.TButton')
        pause_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

        next_btn = ttk.Button(self.window, text=' >> ', width=self.button_width,
                              command=self.next, style='my.TButton')
        next_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

        like_btn = ttk.Button(self.window, text='+', width=self.button_width,
                                  command=self.like, style='my.TButton')
        like_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

    def set_playing(self, playing: bool):
        self.playing = playing

    def previous(self):
        """
        Go to the previous song in the playlist
        """
        try:
            self.client.previous()
            self.callback("previous")
            self.playing = True
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                try:
                    self.client.previous(device_id = self.device_id)
                    self.callback("previous")
                    self.playing = True
                except spotipy.exceptions.SpotifyException as e:
                    messagebox.showwarning("Spotify",
                                        "No Device Found. Please open Spotify on your device of choice")
            elif e.reason == 'UNKNOWN':
                print("Cannot play previous if first song listened to")
            elif "The access token expired" in e.msg:
                self.client.refresh_token()
                self.client.play()
                self.callback("play")

    def pause(self):
        """
        Pause the song
        """
        if not self.playing: return
        try:
            self.client.pause()
            self.callback("pause")
            self.playing = False
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                try:
                    self.client.pause(device_id = self.device_id)
                    self.callback("pause")
                    self.playing = False
                except spotipy.exceptions.SpotifyException as e:
                    messagebox.showwarning("Spotify",
                                        "No Device Found. Please open Spotify on your device of choice")
            elif "Restriction violated" in e.msg:
                # the song is already paused
                pass
            elif "The access token expired" in e.msg:
                self.client.refresh_token()
                self.client.pause()
                self.callback("pause")

    def play(self):
        """
        Play the song
        """
        try:
            self.client.play()
            self.callback("play")
            self.playing = True
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                try:
                    self.client.play(device_id = self.device_id)
                    self.callback("play")
                    self.playing = True
                except spotipy.exceptions.SpotifyException as e:
                    messagebox.showwarning("Spotify",
                                        "No Device Found. Please open Spotify on your device of choice")
            elif "Restriction violated" in e.msg:
                # the song is already playing
                pass
            elif "The access token expired" in e.msg:
                self.client.refresh_token()
                self.client.play()
                self.callback("play")

    def next(self):
        """
        Go to the next song
        """
        try:
            self.client.next()
            self.callback("next")
            self.playing = True
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                try:
                    self.client.next(device_id = self.device_id)
                    self.callback("next")
                    self.playing = True
                except spotipy.exceptions.SpotifyException as e:
                    messagebox.showwarning("Spotify",
                                        "No Device Found. Please open Spotify on your device of choice")
            elif "The access token expired" in e.msg:
                self.client.refresh_token()
                self.client.play()
                self.callback("play")

    def like(self):
        """
        Save to spreadsheet when a song is liked
        """
        try:
            currently_playing = self.callback("like")
            self.liked_songs['name'].append(currently_playing['item']['name'])
            self.liked_songs['id'].append(currently_playing['item']['id'])
            self.liked_songs['time'].append(datetime.now())
            self.liked_songs['type'].append(True)
        except TypeError as e:
            # Nothing's playing, cannot like the song
            print(e)
            pass

    def unlike(self):
        """
        Save to spreadsheet when a song is unliked
        """
        try:
            currently_playing = self.callback("like")
            self.liked_songs['name'].append(currently_playing['item']['name'])
            self.liked_songs['id'].append(currently_playing['item']['id'])
            self.liked_songs['time'].append(datetime.now())
            self.liked_songs['type'].append(False)
        except TypeError as e:
            # Nothing's playing, cannot like the song
            print(e)
            pass

    def save_data(self):
        """
        Save the data to Google Drive
        """
        self.db.save_liked_data(self.liked_songs)
