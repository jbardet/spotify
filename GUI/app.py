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

from RescueWakaTime.RescueWakaTime import RescueWakaTime
from Todoist.Todoist import Todoist
from Timer.Timer import Timer
from Spotify.Radar import Radar
# from Calendar.Calendar import Calendar
# from .Fitbit import Fitbit
# from .LastFM import LastFM
from Configs.Parser import Parser

class App(tk.Tk):
    """
    Main class to display all the GUI's function
    """

    def __init__(self):
        Parser.initialize()
        self.launch()

    def launch(self):
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
            print("fail")
            fg_16bit = self.window.winfo_rgb('#464646')
        self.fg_string = "#" + "".join([hex(fg_color >> 8)[2:] for fg_color in fg_16bit])

        # self.window = tk.Tk()
        self.window.title('Plotting in Tkinter')
        self.window.state('zoomed')   #zooms the screen to maxm whenever executed
        self.window.protocol("WM_DELETE_WINDOW", self.exit)
        # self.window.configure(background='')

        today = datetime.datetime.today()
        # objective = 2
        # if the day is a week-end, congratulate the user to put work on week-ends with a pop-up window
        if today.weekday() == 5 or today.weekday() == 6:
            messagebox.showinfo("Congrats!", "You are working on week-ends! Keep the good work!")
            objective = 4
        else:
            objective = float(Parser.get_goal())
        # make 3 frames from the main window
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

        # self.radio_links = ["https://coderadio.freecodecamp.org/",
        #                     "https://musicforprogramming.net/latest/",
        #                     "https://radio.x-team.com/",
        #                     "https://www.lofi.cafe/"]
        # text = "RescueTime"
        # url = "https://www.rescuetime.com/rtx/reports/activities"
        # font= ('Aerial 12')
        # side = "top"
        # add_website_link(self.window, url, text, font, side)
        self.rw_time = RescueWakaTime()
        self.rw_time.build_frame(self.left_frame, self.bg_string, self.fg_string)
        self.rw_time.add_analytics()
        self.todoist = Todoist()
        self.todoist.build_frame(self.upright_frame, self.bg_string, self.fg_string)
        self.todoist.add_tasks()
        self.timer = Timer(self.update)
        self.timer.build_frame(self.downright_frame, objective, self.bg_string, self.fg_string)
        self.window.bind('<Return>', self.timer.enter)
        self.window.bind('<Escape>', self.timer.stop)
        self.radar = Radar()
        self.radar.build_frame(self.middle_frame, self.bg_string, self.fg_string)
        # self.window.bind('<space>', self.radar.spotify_player.play)
        self.radar.plot_radar()
        # # # self.google_calendar(calendar_cr)
        # # # add link to notion: https://www.notion.so/
        # # # maybe onenote as well ?
        # # # import time
        # # # time.sleep(100)
        # # self.lastfm = LastFM(lastfm_cr)
        # # self.lastfm.save_data()
        # self.radar = Radar(spotify_cr, db_cr, self.middle_frame)
        # thd = threading.Thread(target=self.radar.plot_radar)   # timer thread
        # thd.daemon = True
        # thd.start()
        # # self.fitbit = Fitbit(fitbit_cr)
        # # fitbit.get_data()

        # # create a button in the menu that creates a weekly review and saves data into databases
        # # and also on disk
        # # weekly_button = Button(master = self.window, height = 2, width = 10, text = "Weekly Review", command = self.weekly_review)
        # # weekly_button.pack(side=ttk.TOP)
        # # self.weekly_review()

        # self.window.mainloop()

    def update(self):
        self.rw_time.update_analytics()

    def exit(self):
        self.timer.stop()
        self.timer.save_data()
        self.radar.spotify_player.save_data()
        self.window.destroy()
