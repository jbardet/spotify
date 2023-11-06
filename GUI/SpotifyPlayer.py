import tkinter as tk
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
    def __init__(self, window: tk.Frame, spotify_cr: dict):
        self.window = window
        self.playing = False
        self.__spotify_cr = spotify_cr
        self.client = APIClient([self.__spotify_cr['username']], [self.__spotify_cr['client_id']],
            [self.__spotify_cr['client_secret']])

        previous_btn = tk.Button(self.window, text=' << ', bg='gray', font=("Arial", 13),
                            command=self.client.previous)
        previous_btn.pack(side=tk.LEFT)

        play_btn = tk.Button(self.window, text=' |> ', bg='gray', font=("Arial", 13),
                  command=self.client.play)
        play_btn.pack(side=tk.LEFT)

        pause_btn = tk.Button(self.window, text=' || ', bg='gray', font=("Arial", 13),
                            command=self.client.pause)
        pause_btn.pack(side=tk.LEFT)

        next_btn = tk.Button(self.window, text=' >> ', bg='gray', font=("Arial", 13),
                            command=self.client.next)
        next_btn.pack(side=tk.LEFT)



