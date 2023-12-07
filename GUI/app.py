import csv
import logging
import math
import os
import re
import subprocess
import sys
import threading
import numpy as np
import time
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.scrolledtext as ScrolledText
import tkinter.ttk
from tkinter import StringVar, Entry, Label, Button
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.ttk import Style
from typing import Dict, List, Optional, Tuple
import datetime
import pickle
import math
import requests
import threading
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import webbrowser
import datetime
import os.path
import requests
import matplotlib.pyplot as plt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from todoist_api_python.api import TodoistAPI
from tkinter import ttk
from ttkthemes import ThemedTk
from threading import Thread

from RescueWakaTime.RescueWakaTime import RescueWakaTime
from Todoist.Todoist import Todoist
from Timer.Timer import Timer
from Database.Database import Database
from Drive.Drive import Drive
# from Spotify.Radar import Radar
from Spotify.Spotify import Spotify
# from Calendar.Calendar import Calendar
# from .Fitbit import Fitbit
# from .LastFM import LastFM
from Configs.Parser import Parser
from Credentials.Credentials import Credentials

class App(tk.Tk):
    """
    Main class to display all the GUI's function
    """

    def __init__(self):
        """
        Initialize the GUI App and laucnh different function
        """
        import time
        self.start = time.time()
        __db_cr = Credentials.get_database_credentials()
        __db_id =__db_cr['id']
        __db_password = __db_cr['password']

        self.db_thread = Thread(target=self.initiate_db, args=(__db_id, __db_password))
        self.db_thread.start()
        self.launch()

        # self.initiate_db(__db_id, __db_password)

    def initiate_db(self, __db_id, __db_password):
        """
        Initialize the database
        """
        try:
            self.db = Database(__db_id, __db_password)
        except TimeoutError:
            self.db = Drive()
        print("finish db")

    def launch(self):
        """
        Initialize the Window and lunch the different components
        """
        self.setup_theme()

        self.window.title('Plotting in Tkinter')
        self.window.state('zoomed')   #zooms the screen to max whenever executed
        self.window.protocol("WM_DELETE_WINDOW", self.exit)

        self.get_objective()
        self.build_frames()
        self.build_apps()

        # No need to run the mainloop from here but only from the Radar plot
        # self.window.mainloop()

    def build_apps(self):
        """
        Initiate, build and run the composants of the app
        """
        self.rw_time = RescueWakaTime()
        self.rw_time.build_frame(self.left_frame, self.bg_string, self.fg_string)
        self.rw_time.add_analytics()
        self.todoist = Todoist()
        self.todoist.build_frame(self.upright_frame, self.bg_string, self.fg_string)
        self.todoist.add_tasks()
        print("need db")
        self.db_thread.join()
        print(time.time()-self.start)
        start = time.time()
        self.timer = Timer(self.update, self.db)
        self.timer.build_frame(self.downright_frame, self.objective, self.bg_string, self.fg_string)
        # You can use keyboard shortcuts to start and stop the timer
        self.window.bind('<Return>', self.timer.enter)
        self.window.bind('<Escape>', self.timer.stop)
        print(time.time()-start)
        # Spotify takes more time to load so will do it before Timer
        start = time.time()
        self.spotify = Spotify(self.db)
        self.spotify.build_frame(self.middle_frame, self.bg_string, self.fg_string)
        print(time.time()-start)
        # # Espace key is not good because we use it to write in offline work
        # self.window.bind('<space>', self.radar.spotify_player.play)
        # self.radar.plot_radar()
        # self.spotify.radar.window.mainloop()

        # Unused Apps for now
        # self.google_calendar(calendar_cr)
        # self.lastfm = LastFM(lastfm_cr)
        # self.lastfm.save_data()
        # self.fitbit = Fitbit(fitbit_cr)
        # fitbit.get_data()

    def setup_theme(self):
        """
        Initialize the window and buttons with the theme from the config file
        """
        self.window = ThemedTk(theme=Parser.get_tk_theme())
        s = ttk.Style(self.window)
        s.configure('my.TButton', font=('Aerial', 18))
        s.configure('Treeview', rowheight=28)
        # options anchor, background, font, foreground, justify, padding, relief, text, wraplength
        bg = s.lookup("TFrame", "background")  # get the background color of the theme
        self.window.configure(bg=bg)
        bg_16bit = self.window.winfo_rgb(bg)
        self.bg_string = "#" + "".join([hex(bg_color >> 8)[2:] for bg_color in bg_16bit])
        fg = s.lookup("TFrame", "foreground")
        try:
            fg_16bit = self.window.winfo_rgb(fg)
        except tk._tkinter.TclError:
            # sometimes the foreground color is not defined in the theme
            fg_16bit = self.window.winfo_rgb('#464646')
        self.fg_string = "#" + "".join([hex(fg_color >> 8)[2:] for fg_color in fg_16bit])

    def build_frames(self):
        """
        Make the frames from the main window
        """
        # # create a menu that will reload every graph/composants on the menu
        # # it is for when the graphs get wrongly resized
        # self.menu_bar = tk.Menu(self.window)
        # self.window.config(menu=self.menu_bar)
        # self.menu_bar.add_command(label='Reload', command=self.launch)

        self.left_frame = ttk.Frame(self.window)
        self.left_frame.pack(side='left', anchor='c', fill='both', expand=True,
                             padx=5, pady=5)

        self.middle_frame = ttk.Frame(self.window)
        self.middle_frame.pack(side='left', anchor='c', fill='both', expand=True,
                               padx=5, pady=5)

        self.upright_frame = ttk.Frame(self.window)
        self.upright_frame.pack(side='top', anchor='c', fill='both', expand=True,
                                padx=5, pady=(5,0))

        self.downright_frame = ttk.Frame(self.window)
        self.downright_frame.pack(side='bottom', anchor='c', fill='both', expand=True,
                                  padx=5, pady=(0,5))

    def update(self):
        self.rw_time.update_analytics()

    def exit(self):
        self.timer.stop()
        self.timer.save_data()
        self.spotify.save_data()
        self.window.destroy()

    def get_objective(self):
        """
        Get the objective of the day depending on week/weekends
        """
        today = datetime.datetime.today()
        # if the day is a week-end, congratulate the user to put work on week-ends
        # with a pop-up window
        self.objective = float(Parser.get_goal())
        if today.weekday() == 5 or today.weekday() == 6:
            messagebox.showinfo("Congrats!", "You are working on week-ends! Keep the good work!")
            self.objective = math.ceil(self.objective/2)
