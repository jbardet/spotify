import time
import tkinter as tk
from Helpers.helpers import add_website_link, set_plot_color
import numpy as np
import pandas as pd
import requests
import json
import re
from io import StringIO
from datetime import datetime, timedelta
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import tkinter.ttk as ttk
import googleapiclient
import pygsheets
import pandas as pd
import sys
import os
from Configs.Parser import Parser
from Credentials.Credentials import Credentials
from typing import Callable, Tuple, List
from Drive.Drive import Drive
from Database.Database import Database
from threading import Thread

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

class Timer():
    """
    Class to handle the POMODORO timer but also the links to the stretching
    websites
    """

    def __init__(self, callback: Callable, db) -> None:
        """
        Initialize the frame with the timer and the links

        :param callback: the callback function to call when the timer is stopped
                         that will update the plots from the RescueWakaTime window
        :type callback: Callable
        """
        # self.timer_data_file = Parser.get_timer_data_file()
        # self.offline_data_file = Parser.get_offline_work_file()
        self.pomdoro_time = Parser.get_pomodoro()
        self.callback = callback
        self.db = db

    def build_frame(self, window: ttk.Frame, objective: float, bg_string: str, fg_string: str):
        """
        Build the frame for the Timer window

        :param window: the Frame of the Window
        :type window: ttk.Frame
        :param objective: the objective number of hours to work on the day
        :type objective: float
        :param bg_string: the background color
        :type bg_string: str
        :param fg_string: the foreground color
        :type fg_string: str
        """
        db_thread = Thread(target=self.get_total_time)
        db_thread.start()

        self.window = window
        self.min = np.inf
        self.run = False
        self.objective = objective
        self.bg_string = bg_string
        self.fg_string = fg_string
        self.color_theme = Parser.get_plt_theme()
        self.color = plt.get_cmap(self.color_theme)
        self.colormap = self.color(np.linspace(0, 1, 7))[1:-1]

        # Create empty dictionnary that will then create DataFrames
        self.timer_dict = {"event": [],
                           "time": []}

        self.offline_dict = {
            'category': [],
            'description': [],
            'start': [],
            'finish': [],
            'date': []
        }

        self.plot_frame = ttk.Frame(self.window)
        self.plot_frame.pack(side='top', anchor = 'c', fill='both', expand=True)

        db_thread.join()
        # total_time = self.get_total_time()

        self.add_radial_plot()
        self.add_timer()

    def get_total_time(self):
        """
        Get the total time the timer has been running

        :return: the total time the timer has been running
        :rtype: float
        """
        self.load_data()
        self.compute_time()

    def compute_time(self) -> float:
        """
        Gather the sum of the time for all offline_dict entries as well as timer
        data from the day

        :return: the total time the Timer was running on the day
        :rtype: float
        """
        offline_time = 0
        for i in range(len(self.offline_dict['start'])):
            try:
                offline_time += (datetime.strptime(self.offline_dict['finish'][i], "%H:%M") - \
                    datetime.strptime(self.offline_dict['start'][i], "%H:%M")).seconds
            except ValueError:
                    offline_time += (datetime.strptime(self.offline_dict['finish'][i], "%H:%M:%S") - \
                        datetime.strptime(self.offline_dict['start'][i], "%H:%M:%S")).seconds

        timer_time = 0
        for i, event in enumerate(self.timer_dict['event']):
            if i == 0: continue
            if self.timer_dict['event'][i-1] == "start" and \
                (event == 'pause' or event == 'stop' or event == "finish"):
                timer_time += (self.timer_dict['time'][i] - self.timer_dict['time'][i-1]).total_seconds()
        self.total_time = offline_time + timer_time

    def play(self):
        """
        Start the timer if it is not already started otherwise juste play it from
        where we paused
        """
        print(self.run)
        if not self.run:
            self.timer_dict['event'].append("start")
            self.timer_dict['time'].append(datetime.now())
        self.run = True
        if not hasattr(self, 'submit_thread'):
            self.event = threading.Event()
            self.submit_thread = threading.Thread(target=self.submit, args=(self.event,))
            self.submit_thread.daemon = True
            self.submit_thread.start()

    def enter(self, event: tk.Event):
        """
        When the keyboard enter has been pressed, start the timer if it is not
        running else if it runs pause it

        :param event: the keyboard touch clicked
        :type event: tk.Event
        """
        if self.run:
            self.pause()
        else:
            self.play()

    def submit(self, event: tk.Event):
        """
        Start the timer if we click the Start button or the Enter key

        :param event: the keyboard touch or button clicked
        :type event: tk.Event
        """
        try:
            # the input provided by the user
            self.sec = int(self.hour.get())*3600 + int(self.minute.get())*60 + int(self.second.get())
        except:
            print("Please input the right value")
        while self.sec >-1:
            if event.is_set():
                return
            elif not self.run:
                time.sleep(1)
                continue
            mins, secs = divmod(self.sec,60)

            # Converting the input entered in mins or secs to hours,
            # mins ,secs(input = 110 min --> 120*60 = 6600 => 1hr :
            # 50min: 0sec)
            hours=0
            if mins >60:
                hours, mins = divmod(mins, 60)

            # using format () method to store the value up to two decimal places
            self.hour.set("{0:2d}".format(hours))
            self.minute.set("{0:2d}".format(mins))
            self.second.set("{0:2d}".format(secs))

            # updating the GUI window after decrementing the temp value every time
            self.window.update()
            time.sleep(1)

            # when temp value = 0; then a messagebox pop's up
            # with a message: with the stretching links
            if (self.sec == 0):
                self.timer_dict['event'].append("finish")
                self.timer_dict['time'].append(datetime.now())
                toplevel = tk.Toplevel(self.window)
                toplevel.title("Time Countdown")
                toplevel.attributes('-topmost', 'true')
                label = ttk.Label(toplevel,
                                 text="Time's up. Take a break, here are some stretching links:",
                                 font=("Arial",18,""))
                label.pack(side=tk.TOP)
                self.add_links(toplevel)
                self.reset()
                try:
                    del self.event
                except AttributeError:
                    pass
                try:
                    del self.submit_thread
                except AttributeError:
                    pass
                self.compute_time()
                self.add_radial_plot()
                self.callback()

            # after every one sec the value of temp will be decremented by one
            self.sec -= 1

    def pause(self):
        """
        Pause the timer
        """
        print(self.run)
        if self.run:
            self.timer_dict['event'].append("pause")
            self.timer_dict['time'].append(datetime.now())
        # pause the thread
        self.run = False

    def stop(self, event: tk.Event = None):
        """
        Stop the timer
        """
        try:
            if not self.timer_dict['event'][-1] == "stop":
                self.timer_dict['event'].append("stop")
                self.timer_dict['time'].append(datetime.now())
        except IndexError:
            # We haven't started the timer during the session
            pass
        self.run = False
        # stop the thread
        try:
            self.event.set()
        except AttributeError:
            pass
        self.reset()
        # when we close the main window maybe the thread is not running
        try:
            del self.event
            del self.submit_thread
        except AttributeError:
            pass
        self.compute_time()
        self.add_radial_plot()
        self.callback()

    def reset(self):
        """
        Reset the timer to best Pomodoro time
        """
        self.hour.set("00")
        self.minute.set(self.pomdoro_time)
        self.second.set("00")

    def add_timer(self) -> None:
        """
        Add a timer in the upper right part of the GUI
        """
        offline_frame = ttk.Frame(self.window)
        offline_frame.pack(side=tk.TOP, anchor = 'c',fill='both', expand=True)

        offline_label = ttk.Label(offline_frame, text="Enter offline work: ", font=("Aerial",18))
        offline_label.pack(side = tk.TOP)

        self.category = ttk.Entry(offline_frame, font=('Aerial', 14))
        self.category.bind("<Button-1>", lambda e: self.category.delete(0, tk.END))
        self.category.insert(0,'Category')
        self.category.pack(side = tk.TOP)

        self.description = ttk.Entry(offline_frame, font=('Aerial', 14))
        self.description.bind("<Button-1>", lambda e: self.description.delete(0, tk.END))
        self.description.insert(0,'Description')
        self.description.pack(side = tk.TOP)

        self.start = ttk.Entry(offline_frame, font=('Aerial', 14))
        self.start.bind("<Button-1>", lambda e: self.start.delete(0, tk.END))
        self.start.insert(0,'start')
        self.start.pack(side = tk.TOP)

        self.end = ttk.Entry(offline_frame, font=('Aerial', 14))
        self.end.bind("<Button-1>", lambda e: self.end.delete(0, tk.END))
        self.end.insert(0,'end')
        self.end.pack(side = tk.TOP)

        self.date = ttk.Entry(offline_frame, font=('Aerial', 14))
        self.date.insert(0, date.today())
        self.date.pack(side = tk.TOP)

        enter_offline = ttk.Button(offline_frame, text="Enter",
                                   command= self.enter_offline_work,
                                   style='my.TButton')
        enter_offline.pack(side = tk.TOP)

        timer_frame1 = ttk.Frame(self.window)
        timer_frame1.pack(side=tk.TOP, anchor = 'c', fill='both', expand=True)
        timer_frame2 = ttk.Frame(self.window)
        timer_frame2.pack(side=tk.TOP, anchor = 'c', fill='both', expand=True)

        # Declaration of variables
        self.hour=tk.StringVar()
        self.minute=tk.StringVar()
        self.second=tk.StringVar()

        # Setting the default value as 50 minutes (preferred time for a pomodoro)
        self.reset()

        # Use of Entry class to take input from the user
        hourEntry= ttk.Entry(timer_frame1, width=3, font=('Aerial', 18),
                         textvariable=self.hour)
        # place it in upper right corner
        hourEntry.pack(side = tk.LEFT, anchor = 'c', fill='both', expand=True)

        minuteEntry= ttk.Entry(timer_frame1, width=3, font=('Aerial', 18),
                           textvariable=self.minute)
        minuteEntry.pack(side = tk.LEFT, anchor = 'c', fill='both', expand=True)

        secondEntry= ttk.Entry(timer_frame1, width=3, font=('Aerial', 18),
                           textvariable=self.second)
        secondEntry.pack(side = tk.LEFT, anchor = 'c', fill='both', expand=True)

        # Button widget to start the countdown
        btn = ttk.Button(timer_frame2, text='Start', command=self.play, style='my.TButton')
        btn.pack(side = tk.LEFT, anchor = 'c', fill='both', expand=True)
        btn = ttk.Button(timer_frame2, text='Pause', command= self.pause, style='my.TButton')
        btn.pack(side = tk.LEFT, anchor = 'c', fill='both', expand=True)
        btn = ttk.Button(timer_frame2, text='Stop', command= self.stop, style='my.TButton')
        btn.pack(side = tk.LEFT, anchor = 'c', fill='both', expand=True)

    def add_links(self, window: ttk.Frame) -> None:
        """
        Add links to the stretching websites on the GUI

        :param window: the frame to place the links
        :type window: ttk.Frame
        """

        texts = ["healthline", "verywellfit"]
        urls = [
            "https://www.healthline.com/health/deskercise",
            "https://www.verywellfit.com/best-stretches-for-office-workers-1231153"
        ]
        font = ('Aerial', '16', 'underline')
        side = "bottom"

        add_website_link(window, urls[0], texts[0], font, side,
                         fg = self.fg_string, bg=self.bg_string)
        add_website_link(window, urls[1], texts[1], font, side,
                         fg = self.fg_string, bg=self.bg_string)

    def enter_offline_work(self):
        """
        Save offline work to the dictionary before it will be saved to spreadsheet
        It checks the following conditions on entered time:
        - the time entered is valid
        - start time is before end time
        - end time is before 10 minutes from now
        - date is today or before
        - the entered time is not already overlapping with some offline time
            already in the database
        """
        try:
            datetime.strptime(self.start.get(), "%H:%M")
            datetime.strptime(self.end.get(), "%H:%M")
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a valid time")
            return
        conflict = False
        try:
            assert datetime.strptime(self.start.get(), "%H:%M") < \
                datetime.strptime(self.end.get(), "%H:%M"), \
                    "Start time must be before end time"
            assert datetime.strptime(self.end.get(), "%H:%M") < \
                datetime.now() + timedelta(minutes = 10), \
                    "End time must be before 10 minutes from now"
            assert datetime.strptime(self.date.get(), "%Y-%m-%d").date() <= \
                date.today(),"Date must be today or before"

            # check that entered time does not overlap with timer values
            for i, event in enumerate(self.offline_dict['date']):
                if event == datetime.strptime(self.date.get(), "%Y-%m-%d").date():
                    end_before_start = self.offline_dict['finish'][i] < self.start.get()
                    start_after_end = self.offline_dict['start'][i] > self.end.get()
                    start_before_start = self.offline_dict['start'][i] < self.start.get()
                    end_after_end = self.end.get() < self.offline_dict['finish'][i]
                    msg = f"The offline work you want to add is already in the database:\n"
                    msg+= f"Category: {self.offline_dict['category'][i]}\n"
                    msg+= f"Description: {self.offline_dict['description'][i]}\n"
                    msg+= f"Start: {self.offline_dict['start'][i]}\n"
                    msg+= f"End: {self.offline_dict['finish'][i]}\n"
                    msg+= f"Date: {self.offline_dict['date'][i]}\n"
                    assert end_before_start or start_after_end or \
                        (start_before_start and end_after_end), msg

            # check that entered time does not overlap with offline timer values
            for i, event in enumerate(self.timer_dict['event']):
                event_inside_offline_work = datetime.strptime(self.start.get(), "%H:%M") < \
                    self.timer_dict['time'][i]<datetime.strptime(self.end.get(), "%H:%M")
                if event_inside_offline_work:
                    if event == 'start':
                        # we don't want to already have an event that is not finished
                        conflict=True
                        self.ask_user_for_offline_time_issue(i)
                    else:
                        if self.timer_dict['event'][i-1] == 'start':
                            # we don't want to already have an event that is not finished
                            conflict=True
                            self.ask_user_for_offline_time_issue(i-1)
        except AssertionError as e:
            print(e)
            conflict = True
        if not conflict:
            print("Offline time added")
            self.add_offline_work()

    def update_plot(self):
        """
        Update the plot with the new times added
        """
        self.compute_time()
        self.add_radial_plot()

    def add_offline_work(self):
        """
        Add the offline work entered to the dictionary and update the plots
        """
        self.offline_dict['category'].append(self.category.get())
        self.offline_dict['description'].append(self.description.get())
        self.offline_dict['start'].append(self.start.get())
        self.offline_dict['finish'].append(self.end.get())
        self.offline_dict['date'].append(date.today())
        self.update_plot()

    def ask_user_for_offline_time_issue(self, i: int):
        """
        Ask the user whether he wants to delete offline work entered before or
        if he wants to cancel the offline time he wants to add

        :param i: the index of the offline event that overlaps in the dictionary
        :type i: int
        """
        msg = "Start time has been found during the offline work interval you've given.\n"\
                "Do you want me to suppress the timer data?"
        msg_box = tk.messagebox.askquestion('Time Conflict',
                                            msg,
                                            icon='warning')
        if msg_box == "yes":
            self.timer_dict['event'] = self.timer_dict['event'][:i]+self.timer_dict['event'][i+1:]
            self.timer_dict['time'] = self.timer_dict['time'][:i]+self.timer_dict['time'][i+1:]
            self.add_offline_work()
        else:
            return

    def load_data(self):
        """
        Load the data from the Raspberry Pi database or Google Drive spreadsheets
        """
        db_columns, db_value = self.db.get_timer_data()
        # df_drive, _ = self.drive.get_data(self.timer_data_file)
        # df_drive = self.db.get_timer_data()
        retry = True
        while retry:
            retry = False
            try:
                for row in db_value:
                    for i, key in enumerate(db_columns):
                        if key=="time":
                            self.timer_dict[key].append(parse_timestamp(row[i]))
                        else:
                            self.timer_dict[key].append(row[i])
            except KeyError:
                # there is no data in the spreadsheet
                pass
            except TypeError:
                print("Fail to load timer data, retrying")
                retry = True
        self.timer_suppress = len(self.timer_dict["event"])

        # df_drive, _ = self.drive.get_data(self.offline_data_file)
        db_columns, db_value = self.db.get_offline_data()
        retry = True
        while retry:
            retry = False
            try:
                for row in db_value:
                    for i, key in enumerate(db_columns):
                        if key=="date":
                            self.offline_dict[key].append(datetime.strptime(row[i], '%Y-%m-%d').date())
                        else:
                            self.offline_dict[key].append(row[i])
            except KeyError:
                # there is no data in the spreadsheet
                pass
            except TypeError:
                print("Fail to load offline data, retrying")
                retry = True
        self.offline_suppress = len(self.offline_dict["category"])

    def save_data(self):
        """
        Save data to the Google Drive spreadsheet
        """
        self.db.save_timer_data(self.timer_dict, self.timer_suppress)
        # self.drive.save_data(self.timer_data_file, self.timer_dict, self.timer_suppress)
        self.db.save_offline_data(self.offline_dict, self.offline_suppress)

    def add_radial_plot(self):
        """
        Make the radial plot and add to the GUI

        :param time: time we already have done [s]
        :type time: float
        """
        # I want a radial plot that represents a progress bar from the time we
        # already have done to the objective
        try:
            self.canvas.get_tk_widget().destroy()
        except (AttributeError, tk.TclError):
            # no widget drawn yet
            pass
        ring_width = 0.3
        outer_radius = 1.5
        inner_radius = outer_radius - ring_width

        # set up plot
        value = self.total_time/3600
        ring_arrays = calculate_rings(value, self.objective)
        fig, ax = plt.subplots()

        # we add a second radial plot when we go beyond 100%
        if value > self.objective:
            outer_edge_color = None
            inner_edge_color = self.fg_string
        else:
            outer_edge_color, inner_edge_color = [self.fg_string, None]

        try:
            outer_ring, _ = ax.pie(ring_arrays[0], radius=1.5,
                                colors=[self.colormap[-1], self.colormap[0]],
                                startangle = 90,
                                counterclock = False)
            plt.setp(outer_ring, width=ring_width, edgecolor=outer_edge_color)
        except ValueError:
            pass
        try:
            inner_ring, _ = ax.pie(ring_arrays[1],
                                    radius=inner_radius,
                                    colors=[self.colormap[-2], self.colormap[1]],
                                    startangle = 90,
                                    counterclock = False)
            plt.setp(inner_ring, width=ring_width, edgecolor=inner_edge_color)
        except ValueError:
            pass

        # add labels and format plots
        add_center_label(value, self.objective, self.fg_string)
        add_current_label(value, self.objective, self.fg_string)
        add_sub_center_label(self.objective, self.fg_string)
        ax.axis('equal')
        plt.margins(0,0)
        plt.autoscale('enable')
        fig, self.ax = set_plot_color(fig, ax, self.fg_string)
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.canvas.get_tk_widget().config(bg=self.bg_string)
        self.canvas.draw()
        # self.window.update()

def calculate_rings(value: float, objective: float) -> List[List[int]]:
    """
    Create an array structure for rings

    :param value: current metric value
    :type value: float
    :param objective: target metric value
    :type objective: float
    :return: the values to put inside the radial graphs
    :rtype: List[List[int]]
    """
    if value < objective:
        rings=[[value,objective-value],[0,0]]
    elif value / objective < 2:
        rings=[[value,0],[value % objective, objective-value % objective]]
    else:
        rings = [[0,0],[0,0]]
    return rings

def horizontal_aligner(value: float, objective: float) -> str:
    """
    Determine if the label for the rotating number label should be left/center/right

    :param value: current metric value
    :type value: float
    :param objective: target metric value
    :type objective: float
    :return: where to place the label horizontally
    :rtype: str
    """
    metric = 1.0 * value % objective / objective
    if metric in (0, 0.5):
        align = 'center'
    elif metric < 0.5:
        align = 'left'
    else:
        align = 'right'
    return align

def vertical_aligner(value: float, objective: float) -> str:
    """
    Determine if the label for the rotating number label should be left/center/right

    :param value: current metric value
    :type value: float
    :param objective: target metric value
    :type objective: float
    :return: where to place the label vertically
    :rtype: str
    """
    metric = 1.0 * value, objective % objective / objective
    if metric[0] < 0.25:
        align = 'bottom'
    elif metric[0] < 0.75:
        align = 'top'
    elif metric[0] > 0.75:
        align = 'bottom'
    else:
        align = 'center'
    return align

def add_center_label(value: float, objective: float, color: str) -> plt.text:
    """
    Add the center label to show the percentage of the objective we have done

    :param value: current metric value
    :type value: float
    :param objective: target metric value
    :type objective: float
    :param color: the color of the label
    :type color: str
    :return: the proper text label at the appropriate position
    :rtype: plt.text
    """
    percent = str(round(1.0*value/objective*100,1)) + '%'
    return plt.text(0,
           0.2,
           percent,
           horizontalalignment='center',
           verticalalignment='center',
           fontsize = 40,
           color=color,
           family = 'sans-serif')

def add_current_label(value: float, objective: float, color: str) -> plt.text:
    """
    Add the label to show the metric we have done

    :param value: current metric value
    :type value: float
    :param objective: target metric value
    :type objective: float
    :param color: the color of the label
    :type color: str
    :return: the proper text label at the appropriate position
    :rtype: plt.text
    """
    return plt.text(1.5 * np.cos(0.5 *np.pi - 2 * np.pi * (float(value) % objective /objective)),
            1.5 * np.sin(0.5 *np.pi - 2 * np.pi * (float(value) % objective / objective)),
                    str(round(value, 2)),
                    horizontalalignment=horizontal_aligner(value, objective),
                    verticalalignment=vertical_aligner(value, objective),
                    fontsize = 20,
                    color=color,
                    family = 'sans-serif')

def add_sub_center_label(objective: float, color: str) -> plt.text:
    """
    Add the center label to show the objective of the day

    :param objective: target metric value
    :type objective: float
    :param color: the color of the label
    :type color: str
    :return: the proper text label at the appropriate position
    :rtype: plt.text
    """
    amount = 'Goal: ' + str(objective) + 'h'
    return plt.text(0,
            -.1,
            amount,
            color=color,
            horizontalalignment='center',
            verticalalignment='top',
            fontsize = 22,family = 'sans-serif')

def parse_timestamp(timestamp):
    return datetime(*[int(x) for x in re.findall(r'\d+', timestamp)])
