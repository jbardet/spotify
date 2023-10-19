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
from radar import Radar
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

def open_url(url):
    webbrowser.open_new_tab(url)

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
        self.rescue_time()
        self.todo_list()
        self.set_timer()
        # # self.google_calendar()
        # # add link to notion: https://www.notion.so/
        # # maybe onenote as well ?
        # # import time
        # # time.sleep(100)
        Radar(self.middle_frame).plot_radar()

        self.window.mainloop()

    def todo_list(self):
        # api = TodoistAPI("")
        # today = datetime.datetime.now()
        # after_tomorrow = f"{today.month}/{today.day+2}"
        # try:
        #     # api.get_projects(project_id = '2313332067')
        #     tasks = api.get_tasks( #project_id = '2313332067',
        #                         #   section_id = '137257370',
        #                           filter = f"due before: {after_tomorrow} & #Work & /Work TODO") # due today
        #     print(tasks)
        # except Exception as error:
        #     print(error)
        # with open("tasks.txt", "wb") as file:
        #     pickle.dump(tasks, file)
        # add the links to the stretching exercises:
        todoist_label = Label(self.upright_frame, text= "Todoist", cursor= "hand2", foreground= "green", font= ('Aerial 12'))
        todoist_label.pack(side = tk.TOP)
        url = "https://todoist.com/app/project/2313332067"
        todoist_label.bind("<Button-1>", lambda e:open_url(url))
        with open("tasks.txt", "rb") as file:
            tasks = pickle.load(file)
        # projects -> list of length 4 wit each being a Project object
        # class attributes: dict_keys(['color', 'comment_count', 'id', 'is_favorite', 'is_inbox_project', 'is_shared', 'is_team_inbox', 'name', 'order', 'parent_id', 'url', 'view_style'])
        # self.tasks = []
        # Define the function that changes the color of the selected item
        def change_color():
            # Get the index of the selected item
            active_selection = self.tasks_listbox.curselection()

            # Change the background color of the selected item
            # if green change to red and if red change to white
            if active_selection:
                # print(active_selection)
                # self.tasks_listbox.itemconfig(active_selection, bg='green')
                if self.tasks_listbox.itemcget(active_selection, "background") == "green":
                    self.tasks_listbox.itemconfig(active_selection, bg=self.task_colors[active_selection[0]])
                else:
                    self.tasks_listbox.itemconfig(active_selection, bg='green')
        self.tasks_listbox = tk.Listbox(self.upright_frame, bg='white',
                                        height=10, width=40, font=('Arial', 18),
                                        justify='center')
        self.tasks_listbox.pack(side = tk.TOP)
        colors = ["yellow", "blue", "orange", "red"]
        self.task_colors = []
        for i, task in enumerate(tasks):
            due_date = task.due.date.split("-")
            due_date = datetime.date(eval(due_date[0]),
                                     eval(due_date[1]),
                                     eval(due_date[2]))
            color = colors[task.priority-1]
            self.task_colors.append(color)
            # def change_color(i):
            #     # Get the active selection
            #     active_selection = self.tasks_listbox.curselection()

            #     # Check if the active selection matches the index i
            #     if active_selection == (i,):
            #         # Get the task label and change its color
            #         task_label = self.tasks[i]
            #         if task_label['bg'] == color:
            #             task_label.configure(bg='green')
            #         else:
            #             task_label.configure(bg=color)
            # task_label = tk.Button(self.upright_frame,
            #                       text = task.content+"due: "+str((due_date-datetime.date.today()).days),
            #                       bg = color,
            #                       command = lambda: change_color(i))
            # task_label.pack(side = tk.TOP)
            # self.tasks.append(task_label)
            # # # add a tick box to validate the task
            # # tick_box = tk.Checkbutton(self.upright_frame, text='')
            # # tick_box.pack(side=tk.TOP)
            self.tasks_listbox.insert(i,
                                      task.content+" due: "+str((due_date-datetime.date.today()).days+1))
            self.tasks_listbox.itemconfig(i, {'bg':color})
        self.tasks_listbox.bind('<<ListboxSelect>>', lambda event: change_color())

    def google_calendar(self):
        # see https://developers.google.com/calendar/api/quickstart/python

        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        id_client = ""
        client_secret = ""
        token_url = "https://accounts.google.com/o/oauth2/v2/auth"
        url = "https://www.googleapis.com/calendar/v3"
        redirect_uri = "http://localhost:8080"
        api_call = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
        link_to_today = "https://calendar.google.com/calendar/u/0/r/day"

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId='ca7ac9827d5d3f5298bdb789244b3d29bd389cecb3abc016143865c81549bbd6@group.calendar.google.com',
                                                  timeMin=now, maxResults=10,
                                                  singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            today_events = []
            # Prints the start and name of the next 10 events
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                # if the event is today keep it
                if start_time.date() == datetime.datetime.today().date():
                    end = event['start'].get('dateTime', event['start'].get('date'))
                    print(start)
                    try:
                        title = event['summary']
                    except KeyError:
                        title = "No title"
                    try:
                        description = event['description']
                    except KeyError:
                        description = "No description"
                    today_events.append([title, description, start, end])

        except HttpError as error:
            print('An error occurred: %s' % error)

        print(today_events)

    def rescue_time(self):
        """
        Integrate a Rescue time window to see your daily activity
        """
        key = ""
        # for the analytic data:
        # perspective -> rank or interval
        # resolution_time -> [ 'month' | 'week' | 'day' | 'hour' | 'minute' ]
        # restrict_begin
        # restrict_end
        # restrict_kind -> [ 'category' | 'activity' | 'productivity' | 'document' ]
        # restrict_thing -> name (of category, activity, or overview)
        # restrict_thingy
        # restrict_source_type -> [ 'computers' | 'mobile' | 'offline' ]
        # restrict_schedule_id -> id (integer id of user's schedule/time filter)
        productivity_call = f"https://www.rescuetime.com/anapi/data?key={key}&perspective=interval&restrict_kind=productivity&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"
        overview_call = f"https://www.rescuetime.com/anapi/data?key={key}&perspective=rank&restrict_kind=overview&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"

        # Daily summary feed
        daily_summary = f"https://www.rescuetime.com/anapi/daily_summary_feed?key={key}"

        # Alerts feed api Alerts are a premium feature and as such the API will always return zero results for users on the RescueTime Lite plan.
        # Highlights also premium, FocusTime Feed API also
        # alert_call = f"https://www.rescuetime.com/anapi/alerts_feed?key={key}&op=list"

        # FocusTime Trigger API -> start/end FocusTime on active devices as an alternative to starting/ending it manually from the desktop app.
        # duration is in min and -1 if until end of the day (return 200 if ok, 400 if fails)
        start_call = f"https://www.rescuetime.com/anapi/start_focustime?key={key}&duration=30"
        end_call = f"https://www.rescuetime.com/anapi/end_focustime?key={key}"

        # Offline Time POST API -> add offline time to a user's account (200/400), t in minutes, detail is optional
        offline_call = f"https://www.rescuetime.com/anapi/offline_time_post?key={key}"
        offline_json = {
            "start_time": "2020-01-01 09:00:00",
            "duration": 60,
            "activity_name": "Meeting",
            "activity_details": "Daily Planning"
            }

        # # productivity_rank_call2 = f"https://www.rescuetime.com/anapi/data?key={key}&perspective=rank&restrict_kind=productivity&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"
        # # response = requests.get(productivity_rank_call2)
        # # data_prod_rank = response.json()

        rescue_label = Label(self.left_frame, text= "RescueTime", cursor= "hand2", foreground= "green", font= ('Aerial 12'))
        rescue_label.pack(side = tk.TOP)
        url = "https://www.rescuetime.com/rtx/reports/activities"
        rescue_label.bind("<Button-1>", lambda e:open_url(url))

        # # with open("data_prod_rank.pickle", "wb") as file:
        # #     pickle.dump(data_prod_rank, file)
        with open('data_prod_rank.pickle', 'rb') as handle:
            data_prod_rank = pickle.load(handle)

        # make a horizontal bar chart with the data
        rows = data_prod_rank['rows']
        data_to_plot = [[] for _ in range(len(rows))]
        for row in data_prod_rank['rows']:
            data_to_plot[2-row[-1]] = [row[-1], row[1]]
        # data_to_plot = [np.array(data_prod_rank['rows'])[:,-1], np.array(data_prod_rank['rows'])[:,1]]
        # sort the list by order of the the first sublist values
        # data_to-plot
        # data_to_plot = [[data_to_plot[i, 0], data_to_plot[i, 1]] for i in np.arg]
        # data_to_plot.sort()
        red = Color("green")
        colors = list(red.range_to(Color("red"),5))
        colors = [col.hex for col in colors]
        fig, (self.ax) = plt.subplots(1, 1, figsize=(5,2))
        plt.barh(np.array(data_to_plot)[:,0], np.array(data_to_plot)[:,1]/3600, color=colors)
        canvas = FigureCanvasTkAgg(fig, master = self.left_frame) #, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side = tk.TOP)

        # productivity_call6 = f"https://www.rescuetime.com/anapi/data?key={key}&perspective=rank&restrict_kind=document&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"
        # response6 = requests.get(productivity_call6)
        # data6 = response6.json()

        # with open("data6.pickle", "wb") as file:
        #     pickle.dump(data6, file)
        with open('data6.pickle', 'rb') as handle:
            data6 = pickle.load(handle)
        # print(data6)

        df = pd.DataFrame(data6['rows'], columns = ['rank', 'time', 'people', 'activity', 'document', 'category', 'productivity'])
        # sort the serie by value
        top_ten = df.groupby("category").sum()['time'].sort_values(ascending=False)[:10]
        # make a vertical bar chart with the data
        # data_to_plot = [[] for _ in range(len(rows))]
        red = Color("green")
        colors = list(red.range_to(Color("red"),5))
        colors = [col.hex for col in colors]
        plot_colors = [colors[2-df[df['category'] == cat]['productivity'].iloc[0]] for cat in top_ten.keys()]
        fig, (self.ax) = plt.subplots(1, 1, figsize=(5,4))
        plt.bar(top_ten.keys(), top_ten.values/3600, color=plot_colors)
        # plot the labels with angle
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master = self.left_frame) #, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side = tk.TOP)

        # add button to start/end rescue time call
        def start_rescue_time():
            if self.rescue_time_is_on:
                call = f"https://www.rescuetime.com/anapi/end_focustime?key={key}"
                self.rescue_time_is_on = True
                self.rescue_time_button.configure(text = "Start Rescue Time")
            else:
                call = f"https://www.rescuetime.com/anapi/start_focustime?key={key}&duration=-1"
                self.rescue_time_is_on = False
                self.rescue_time_button.configure(text = "End Rescue Time")
            response = requests.get(call)
            if response.status_code == 404:
                print("rescue_time_is_on is wrong ")
            # data_prod_rank = response.json()
        self.rescue_time_is_on = True
        text = "Start Rescue Time" if self.rescue_time_is_on else "End Rescue Time"
        self.rescue_time_button = tk.Button(self.left_frame, text = text, command = start_rescue_time)
        self.rescue_time_button.pack(side = tk.TOP)
        print("oe")

    def exit(self):
        self.window.destroy()

    def set_timer(self):
        """
        Creates a timer in the upper right part of the GUI
        """
        # Declaration of variables
        self.hour=StringVar()
        self.minute=StringVar()
        self.second=StringVar()

        # setting the default value as 0
        self.hour.set("00")
        self.minute.set("50")
        self.second.set("00")

        # set a label to explain the timer
        timer_label = Label(self.downright_frame, text="POMODORO: ", font=("Arial",18,""))
        timer_label.pack(side = tk.TOP)

        # Use of Entry class to take input from the user
        hourEntry= Entry(self.downright_frame, width=3, font=("Arial",18,""),
                        textvariable=self.hour)
        # hourEntry.place(x=200,y=20)
        # place it in upper right corner
        hourEntry.pack(side = tk.LEFT)

        minuteEntry= Entry(self.downright_frame, width=3, font=("Arial",18,""),
                        textvariable=self.minute)
        # minuteEntry.place(x=240,y=20)
        minuteEntry.pack(side = tk.LEFT)

        secondEntry= Entry(self.downright_frame, width=3, font=("Arial",18,""),
                        textvariable=self.second)
        # secondEntry.place(x=280,y=20)
        secondEntry.pack(side = tk.LEFT)

        # button widget
        btn = Button(self.downright_frame, text='Set Time Countdown', font=("Arial",18),
                    command= self.submit)
        # btn.place(x=300,y = 20)
        btn.pack(side = tk.LEFT)

        # add the links to the stretching exercises:
        stretching_links = [
            Label(self.downright_frame, text= "healthline", cursor= "hand2", foreground= "green", font= ('Aerial 12')),
            Label(self.downright_frame, text= "verywellfit", cursor= "hand2", foreground= "green", font= ('Aerial 12')),
        ]
        [label.pack(side = tk.BOTTOM) for label in stretching_links]
        urls = [
            "https://www.healthline.com/health/deskercise",
            "https://www.verywellfit.com/best-stretches-for-office-workers-1231153"
        ]
        # [label.bind("<Button-1>", lambda e:open_url(urls[i])) for i, label in enumerate(stretching_links)]
        stretching_links[0].bind("<Button-1>", lambda e:open_url(urls[0]))
        stretching_links[1].bind("<Button-1>", lambda e:open_url(urls[1]))

    def submit(self):
        try:
            # the input provided by the user is
            # stored in here :temp
            temp = int(self.hour.get())*3600 + int(self.minute.get())*60 + int(self.second.get())
        except:
            print("Please input the right value")
        while temp >-1:
            mins,secs = divmod(temp,60)

            # Converting the input entered in mins or secs to hours,
            # mins ,secs(input = 110 min --> 120*60 = 6600 => 1hr :
            # 50min: 0sec)
            hours=0
            if mins >60:
                hours, mins = divmod(mins, 60)

            # using format () method to store the value up to
            # two decimal places
            self.hour.set("{0:2d}".format(hours))
            self.minute.set("{0:2d}".format(mins))
            self.second.set("{0:2d}".format(secs))

            # updating the GUI window after decrementing the
            # temp value every time
            self.window.update()
            time.sleep(1)

            # when temp value = 0; then a messagebox pop's up
            # with a message:"Time's up"
            if (temp == 0):
                messagebox.showinfo("Time Countdown", "Time's up ")

            # after every one sec the value of temp will be decremented
            # by one
            temp -= 1


    # # Determine the origin by clicking
    # def getorigin(self, eventorigin):
    #     global x0,y0
    #     x0 = eventorigin.x
    #     y0 = eventorigin.y
    #     print(x0,y0)
    #     # self.windie.bind("<Button 1>",getextentx)
