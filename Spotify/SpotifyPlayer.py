import tkinter as tk
from tkinter import ttk
import spotipy

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
    def __init__(self, window: tk.Frame, spotify_cr: dict, fg_string, bg_string):
        self.window = window
        self.playing = False
        self.__spotify_cr = spotify_cr
        self.fg_string = fg_string
        self.bg_string = bg_string
        self.client = APIClient([self.__spotify_cr['username']], [self.__spotify_cr['client_id']],
            [self.__spotify_cr['client_secret']])

        previous_btn = ttk.Button(self.window, text=' << ',
                                  command=self.client.previous, style='my.TButton')
        previous_btn.pack(side=tk.LEFT, anchor='c', fill='both', expand=True)

        play_btn = ttk.Button(self.window, text=' |> ',
                              command=self.client.play, style='my.TButton')
        play_btn.pack(side=tk.LEFT, anchor='c', fill='both', expand=True)

        pause_btn = ttk.Button(self.window, text=' || ',
                               command=self.client.pause, style='my.TButton')
        pause_btn.pack(side=tk.LEFT, anchor='c', fill='both', expand=True)

        next_btn = ttk.Button(self.window, text=' >> ',
                              command=self.client.next, style='my.TButton')
        next_btn.pack(side=tk.LEFT, anchor='c', fill='both', expand=True)

    def play(self, event=None):
        if self.playing:
            self.client.pause()
        else:
            self.client.play()



