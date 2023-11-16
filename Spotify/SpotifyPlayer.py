import tkinter as tk
from tkinter import ttk
import spotipy
from tkinter import messagebox
from Credentials.Credentials import Credentials
from datetime import datetime
from Drive.Drive import Drive
from typing import Callable, Dict

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

class SpotifyPlayer():
    """
    SpotifyPlayer widget to play songs, pause, ...
    """
    def __init__(self,
                 window: tk.Frame,
                 callback: Callable,
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
        self.playing = False
        self.callback = callback
        self.__spotify_cr = spotify_cr
        self.fg_string = fg_string
        self.bg_string = bg_string
        self.client = APIClient([self.__spotify_cr['username']],
                                [self.__spotify_cr['client_id']],
                                [self.__spotify_cr['client_secret']])
        self.liked_songs = {'name': [], 'id': [], 'time': [], 'like': []}
        self.currently_playing = self.client.get_current_track()
        self.button_width = 6

        unlike_btn = ttk.Button(self.window, text='-', width=self.button_width,
                                  command=self.unlike, style='my.TButton')
        unlike_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

        shuffle_btn = ttk.Button(self.window, text='~', width=self.button_width,
                                  command=self.shuffle, style='my.TButton')
        shuffle_btn.pack(side=tk.LEFT, anchor='c', fill='y', expand=True)

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

    def shuffle(self):
        """
        Shuffle the songs when playing the playlist
        """
        try:
            self.client.shuffle()
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                messagebox.showwarning("Spotify",
                                       "No Device Found. Please open Spotify on your device of choice")

    def previous(self):
        """
        Go to the previous song in the playlist
        """
        try:
            self.client.previous()
            self.callback("previous")
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                messagebox.showwarning("Spotify",
                                       "No Device Found. Please open Spotify on your device of choice")
            elif e.reason == 'UNKNOWN':
                print("Cannot play previous if first song listened to")

    def pause(self):
        """
        Pause the song
        """
        try:
            self.client.pause()
            self.callback("pause")
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                messagebox.showwarning("Spotify",
                                       "No Device Found. Please open Spotify on your device of choice")

    def play(self):
        """
        Play the song
        """
        try:
            self.client.play()
            self.callback("play")
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                messagebox.showwarning("Spotify",
                                       "No Device Found. Please open Spotify on your device of choice")

    def next(self):
        """
        Go to the next song
        """
        try:
            self.client.next()
            self.callback("next")
        except spotipy.exceptions.SpotifyException as e:
            if e.reason == 'NO_ACTIVE_DEVICE':
                messagebox.showwarning("Spotify",
                                       "No Device Found. Please open Spotify on your device of choice")

    def like(self):
        """
        Save to spreadsheet when a song is liked
        """
        self.liked_songs['name'].append(self.currently_playing['item']['name'])
        self.liked_songs['id'].append(self.currently_playing['item']['id'])
        self.liked_songs['time'].append(datetime.now())
        self.liked_songs['like'].append(True)

    def unlike(self):
        """
        Save to spreadsheet when a song is unliked
        """
        self.liked_songs['name'].append(self.currently_playing['item']['name'])
        self.liked_songs['id'].append(self.currently_playing['item']['id'])
        self.liked_songs['time'].append(datetime.now())
        self.liked_songs['like'].append(False)

    def save_data(self):
        """
        Save the data to Google Drive
        """
        Drive().save_data("liked_songs.csv", self.liked_songs)
