import sys
import os
import numpy as np
import flask
import tkinter
import tkinter.filedialog
import tkinter.scrolledtext
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
from tkinter import ttk
from ttkthemes import ThemedTk
from rauth import OAuth2Service
from urllib.parse import parse_qsl
from datetime import timedelta as td
import tkinter.ttk as ttk
from ttkwidgets import CheckboxTreeview
import pygsheets
import pandas as pd
import warnings
from wordcloud import WordCloud
from typing import Dict
import tkinter.ttk as ttk
import json
import math
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import spotipy

def get_script_folder():
    # path of main .py or .exe when converted with pyinstaller
    if getattr(sys, 'frozen', False):
        script_path = os.path.dirname(sys.executable)
    else:
        script_path = os.path.dirname(
            os.path.abspath(sys.modules['__main__'].__file__)
        )
    return script_path

def get_data_folder():
    # path of your data in same folder of main .py or added using --add-data
    if getattr(sys, 'frozen', False):
        data_folder_path = sys._MEIPASS
    else:
        data_folder_path = os.path.dirname(
            os.path.abspath(sys.modules['__main__'].__file__)
        )
    return data_folder_path

try:
    from GUI.app import App
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(get_script_folder()))
    print(sys.path)
    # try:
    from GUI.app import App
    # except ModuleNotFoundError:
    #     try:
    #         from app import App
    #     except ImportError:
    #         # print(sys.path)
    #         # sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    #         # print(sys.path)
    #         # print(get_script_folder())
    #         # print(get_data_folder())
    #         try:
    #             from GUI.app import App
    #         except ModuleNotFoundError:
    #             try:
    #                 from app import App
    #             except ModuleNotFoundError:
    #                 try:
    #                     from .GUI.app import App
    #                 except ImportError:
    #                     from .app import App

def main() -> None:
    App()

if __name__ == '__main__':
    main()
