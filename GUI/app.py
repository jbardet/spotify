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
import json
from colour import Color
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

from RescueWakaTime import RescueWakaTime
from Todoist import Todoist
from Timer import Timer
from Calendar import Calendar
from Radar import Radar
from Fitbit import Fitbit

class App(tk.Tk):
    """
    Main class to display all the GUI's function
    """

    def __init__(self):
        self.launch()

    def launch(self):
        self.window = tk.Tk()
        self.window.title('Plotting in Tkinter')
        self.window.state('zoomed')   #zooms the screen to maxm whenever executed

        # make 3 frames from the main window
        self.left_frame = tk.Frame(self.window, bg='white')
        self.left_frame.pack(side='left', fill='both', expand=True)

        self.middle_frame = tk.Frame(self.window, bg='white')
        self.middle_frame.pack(side='left', fill='both', expand=True)

        self.upright_frame = tk.Frame(self.window, bg='white')
        self.upright_frame.pack(side='top', anchor='n', fill='both', expand=True)

        self.downright_frame = tk.Frame(self.window, bg='white')
        self.downright_frame.pack(side='bottom', anchor='s', fill='both', expand=True)

        with open("credentials.json", "r") as file:
            data = json.load(file)
            fitbit_cr = data['fitbit']
            rescue_cr = data['RescueTime']
            waka_cr = data['WakaTime']
            todoist_cr = data['Todoist']
            calendar_cr = data['calendar']
            db_cr = data['database']
            spotify_cr = data['spotify']

        # self.radio_links = ["https://coderadio.freecodecamp.org/",
        #                     "https://musicforprogramming.net/latest/",
        #                     "https://radio.x-team.com/",
        #                     "https://www.lofi.cafe/"]

        # # # plot_button = Button(master = window,command = Radar(window).plot_radar())
        # # #, height = 2, width = 10, text = "Plot")
        # # # plot_button.pack()
        # self.rw_time = RescueWakaTime(rescue_cr, waka_cr, self.left_frame)
        # self.rw_time.add_analytics()
        # self.todoist = Todoist(todoist_cr, self.upright_frame)
        # self.todoist.add_tasks()
        # self.timer = Timer(self.downright_frame)
        # # # # self.google_calendar(calendar_cr)
        # # # # add link to notion: https://www.notion.so/
        # # # # maybe onenote as well ?
        # # # # import time
        # # # # time.sleep(100)
        # self.radar = Radar(spotify_cr, db_cr, self.middle_frame)
        # self.radar.plot_radar()
        # self.fitbit = Fitbit(fitbit_cr)
        # fitbit.get_data()

        # create a button in the menu that creates a weekly review and saves data into databases
        # and also on disk
        # weekly_button = Button(master = self.window, height = 2, width = 10, text = "Weekly Review", command = self.weekly_review)
        # weekly_button.pack(side=tk.TOP)
        self.weekly_review()

        self.window.mainloop()

    def weekly_review(self):
        with open("credentials.json", "r") as file:
            data = json.load(file)
            fitbit_cr = data['fitbit']
            rescue_cr = data['RescueTime']
            waka_cr = data['WakaTime']
            todoist_cr = data['Todoist']
            calendar_cr = data['calendar']
            db_cr = data['database']
            spotify_cr = data['spotify']
        with open('saves.txt', 'r') as file:
            last_save = file.read()
        # self.rw_time = RescueWakaTime(rescue_cr, waka_cr, self.left_frame)
        # self.rw_time.save_data()
        # self.todoist = Todoist(todoist_cr, self.upright_frame)
        # self.todoist.save_data(last_save)
        # self.radar = Radar(spotify_cr, db_cr, self.middle_frame)
        # self.radar.save_data()
        self.fitbit = Fitbit(fitbit_cr)
        self.fitbit.save_data()
        self.generate_weekly_report()

    def generate_weekly_report(self):
        pass

    def exit(self):
        self.window.destroy()
