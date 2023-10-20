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

from RescueTime import RescueTime
from Todoist import Todoist
from Timer import Timer
from Calendar import Calendar
from Radar import Radar

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

        # self.radio_links = ["https://coderadio.freecodecamp.org/",
        #                     "https://musicforprogramming.net/latest/",
        #                     "https://radio.x-team.com/",
        #                     "https://www.lofi.cafe/"]

        # # plot_button = Button(master = window,command = Radar(window).plot_radar())
        # #, height = 2, width = 10, text = "Plot")
        # # plot_button.pack()
        # RescueTime("", self.left_frame).add_analytics()
        # Todoist("", self.upright_frame).add_tasks()
        # Timer(self.downright_frame)
        # # # self.google_calendar()
        # # # add link to notion: https://www.notion.so/
        # # # maybe onenote as well ?
        # # # import time
        # # # time.sleep(100)
        Radar(self.middle_frame).plot_radar()

        self.window.mainloop()

    def exit(self):
        self.window.destroy()
