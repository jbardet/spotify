import time
import tkinter as tk
from tkinter import messagebox
from Helpers.helpers import add_website_link, set_plot_color
import numpy as np
import pandas as pd
import requests
import json
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

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

class Timer():
    """
    Class to handle the POMODORO timer but also the links to the stretching
    websites
    """
    def __init__(self, callback) -> None:
        """
        Initialize the frame with the timer and the links

        :param window: the window frame where to place the timer and the links
        :type window: ttk.Frame
        """
        self.timer_data_file = Parser.get_timer_data_file()
        self.offline_data_file = Parser.get_offline_work_file()
        self.callback = callback

    def build_frame(self, window: ttk.Frame, objective: float, bg_string: str, fg_string: str):
        self.window = window
        self.min = np.inf
        self.run = False
        self.objective = objective
        self.bg_string = bg_string
        self.fg_string = fg_string
        self.color_theme = Parser.get_plt_theme()
        self.color = plt.get_cmap(self.color_theme)
        self.colormap = self.color(np.linspace(0, 1, 7))[1:-1]

        # Create empty dataframe
        self.timer_dict = {"event": [],
                           "time": []}

        self.offline_dict = {
            'category': [],
            'description': [],
            'start': [],
            'end': [],
            'date': []
        }

        self.load_data()
        self.plot_frame = ttk.Frame(self.window)
        self.plot_frame.pack(side='top', anchor = 'c', fill='both', expand=True)
        total_time = self.compute_time()
        self.add_radial_plot(total_time)
        self.add_timer()

    def compute_time(self):
        # gather the sum of the time for all offline_dict entries
        offline_time = np.sum([(datetime.strptime(self.offline_dict['end'][i], "%H:%M") - datetime.strptime(self.offline_dict['start'][i], "%H:%M")).seconds for i in range(len(self.offline_dict['start']))])
        timer_time = 0
        for i, event in enumerate(self.timer_dict['event']):
            if i == 0: continue
            if self.timer_dict['event'][i-1] == "start" and (event == 'pause' or event == 'stop' or event == "finish"):
                timer_time += (self.timer_dict['time'][i] - self.timer_dict['time'][i-1]).total_seconds()
        return offline_time + timer_time

    def play(self):
        self.timer_dict['event'].append("start")
        self.timer_dict['time'].append(datetime.now())
        print("play")
        self.run = True
        # print(hasattr(self, 'submit_thread'))
        if not hasattr(self, 'submit_thread'):
            # print("start new one")
            self.event = threading.Event()
            self.submit_thread = threading.Thread(target=self.submit, args=(self.event,))
            self.submit_thread.daemon = True
            self.submit_thread.start()

    def enter(self, event: tk.Event):
        if self.run:
            self.pause()
        else:
            self.play()

    def submit(self, event):
        """
        Start the timer
        """
        try:
            # the input provided by the user is
            # stored in here :temp
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
            if (self.sec == 0):
                self.timer_dict['event'].append("finish")
                self.timer_dict['time'].append(datetime.now())
                toplevel = tk.Toplevel(self.window)
                toplevel.title("Time Countdown")
                toplevel.attributes('-topmost', 'true')
                # toplevel.state('zoomed')
                label = ttk.Label(toplevel,
                                 text="Time's up. Take a break, here are some stretching links:",
                                 font=("Arial",18,""))
                label.pack(side=tk.TOP)
                self.add_links(toplevel)
                self.reset()
                del self.event
                del self.submit_thread
                total_time = self.compute_time()
                self.add_radial_plot(total_time)
                self.callback()

            # after every one sec the value of temp will be decremented
            # by one
            self.sec -= 1

    def pause(self):
        """
        Pause the timer
        """
        print("pause")
        self.timer_dict['event'].append("pause")
        self.timer_dict['time'].append(datetime.now())
        # pause the thread
        self.run = False

    def stop(self, event=None):
        """
        Stop the timer
        """
        print("stop")
        self.run = False
        self.timer_dict['event'].append("stop")
        self.timer_dict['time'].append(datetime.now())
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
        total_time = self.compute_time()
        self.add_radial_plot(total_time)
        self.callback()

    def reset(self):
        self.hour.set("00")
        self.minute.set("50")
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

        # # # Set a label to explain the timer
        # # timer_label = Label(self.window, text="POMODORO: ", font=("Arial",18,""))
        # # timer_label.pack(side = tk.TOP)

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
        """

        texts = ["healthline", "verywellfit"]
        urls = [
            "https://www.healthline.com/health/deskercise",
            "https://www.verywellfit.com/best-stretches-for-office-workers-1231153"
        ]
        font = ('Aerial', '16', 'underline')
        side = "bottom"

        add_website_link(window, urls[0], texts[0], font, side, fg = self.fg_string, bg=self.bg_string)
        add_website_link(window, urls[1], texts[1], font, side, fg = self.fg_string, bg=self.bg_string)

    def enter_offline_work(self):
        try:
            datetime.strptime(self.start.get(), "%H:%M")
            datetime.strptime(self.end.get(), "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid time")
            return
        conflict = False
        try:
            assert datetime.strptime(self.start.get(), "%H:%M") < datetime.strptime(self.end.get(), "%H:%M"), "Start time must be before end time"
            assert datetime.strptime(self.end.get(), "%H:%M") < datetime.now() + timedelta(minutes = 10), "End time must be before 10 minutes from now"
            assert datetime.strptime(self.date.get(), "%Y-%m-%d").date()<=date.today(), "Date must be today or before"
            for i, event in enumerate(self.offline_dict['date']):
                if event == datetime.strptime(self.date.get(), "%Y-%m-%d").date():
                    end_before_start = self.offline_dict['end'][i] < self.start.get()
                    start_after_end = self.offline_dict['start'][i] > self.end.get()
                    start_before_start = self.offline_dict['start'][i] < self.start.get()
                    end_after_end = self.end.get() < self.offline_dict['end'][i]
                    msg = f"The offline work you want to add is already in the database:\n"
                    msg+= f"Category: {self.offline_dict['category'][i]}\n"
                    msg+= f"Description: {self.offline_dict['description'][i]}\n"
                    msg+= f"Start: {self.offline_dict['start'][i]}\n"
                    msg+= f"End: {self.offline_dict['end'][i]}\n"
                    msg+= f"Date: {self.offline_dict['date'][i]}\n"
                    assert end_before_start or start_after_end or (start_before_start and end_after_end), msg
            for i, event in enumerate(self.timer_dict['event']):
                event_inside_offline_work = datetime.strptime(self.start.get(), "%H:%M")<self.timer_dict['time'][i]<datetime.strptime(self.end.get(), "%H:%M")
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
            conflict = True
        if not conflict:
            self.add_offline_work()

    def update_plot(self):
        total_time = self.compute_time()
        self.add_radial_plot(total_time)

    def add_offline_work(self):
        self.offline_dict['category'].append(self.category.get())
        self.offline_dict['description'].append(self.description.get())
        self.offline_dict['start'].append(self.start.get())
        self.offline_dict['end'].append(self.end.get())
        self.offline_dict['date'].append(date.today())
        self.update_plot()

    def ask_user_for_offline_time_issue(self, i):
        msg = "Start time has been found during the offline work interval you've given.\n"\
                "Do you want me to suppress the timer data?"
        msg_box = messagebox.askquestion('Time Conflict',
                                        msg,
                                        icon='warning')
        if msg_box == "yes":
            self.timer_dict['event'] = self.timer_dict['event'][:i]+self.timer_dict['event'][i+1:]
            self.timer_dict['time'] = self.timer_dict['time'][:i]+self.timer_dict['time'][i+1:]
            self.add_offline_work()
        else:
            return

    def load_data(self):
        df_drive, _ = self.get_data(self.timer_data_file)
        retry = True
        while retry:
            retry = False
            try:
                df_drive['time'] = pd.to_datetime(df_drive['time'])
                # find columns where the date is today
                today_work = df_drive[df_drive['time'].dt.date == date.today()]
                for _, row in today_work.iterrows():
                    self.timer_dict["event"].append(row['event'])
                    self.timer_dict["time"].append(row['time'])
            except KeyError:
                pass
            except TypeError:
                print("Fail to load timer data, retrying")
                retry = True
        self.timer_suppress = len(self.timer_dict["event"])

        df_drive, _ = self.get_data(self.offline_data_file)
        # find columns where the date is today
        retry = True
        while retry:
            retry = False
            try:
                df_drive['date'] = pd.to_datetime(df_drive['date'])
                today_work = df_drive[df_drive['date'].dt.date == date.today()]
                for _, row in today_work.iterrows():
                    self.offline_dict["category"].append(row['category'])
                    self.offline_dict["description"].append(row['description'])
                    self.offline_dict["start"].append(row['start'])
                    self.offline_dict["end"].append(row['end'])
                    self.offline_dict["date"].append(row['date'].date())
            except KeyError:
                pass
            except TypeError:
                print("Fail to load offline data, retrying")
                retry = True
        self.offline_suppress = len(self.offline_dict["category"])

    def get_data(self, name):
        # authorization
        try:
            gc = pygsheets.authorize(service_file='Credentials/spotify-402405-59d8f4e06e41.json')
        except FileNotFoundError:
            gc = pygsheets.authorize(service_file=os.path.join(sys.path[-1],
                                                               'Credentials/spotify-402405-59d8f4e06e41.json'))
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        # DO NOT FORGET TO SHARE THE SPREADSHEET
        try:
            sh = gc.open(name)
            #select the first sheet
            wks = sh[0]

            # existing df
            df_drive = wks.get_as_df()
            return df_drive, wks
        except googleapiclient.errors.HttpError:
            print(f"HTTP error when trying to access {name}")
            return None, None
        except pygsheets.exceptions.SpreadsheetNotFound:
            print(f"Spreadsheet {name} not found, will not use/save data")
            return pd.DataFrame(), None

    def save_data(self):
        df_drive, wks = self.get_data(self.timer_data_file)
        df_drive.drop(df_drive.tail(self.timer_suppress).index, inplace = True)
        #update the first sheet with df, starting at cell B2.
        df = pd.DataFrame.from_dict(self.timer_dict)
        df_save = pd.concat([df_drive, df], ignore_index=True)
        wks.set_dataframe(df_save,(0,0))

        df_drive, wks = self.get_data(self.offline_data_file)
        df_drive.drop(df_drive.tail(self.offline_suppress).index, inplace = True)
        #update the first sheet with df, starting at cell B2.
        df = pd.DataFrame.from_dict(self.offline_dict)
        df_save = pd.concat([df_drive, df], ignore_index=True)
        wks.set_dataframe(df_save,(0,0))

    def add_radial_plot(self, time: float) -> None:
        """
        Make the radial plot and add to the GUI, time is in seconds
        """
        # I want a radial plot that represents a progress bar from the time we already have done to the objective
        # the objective is 7.5 hours per day
        # the time is the time we already have done
        # plt.close()
        try:
            self.canvas.get_tk_widget().destroy()
        except AttributeError:
            pass
        # fig = plt.figure(figsize=(4,4))
        # ax = fig.add_subplot(111, polar=True)
        # ax.set_ylim(0, 1)
        # ax.set_yticklabels([])
        # ax.set_xticklabels([])
        # ax.set_theta_zero_location('N')
        # ax.set_theta_direction(-1)
        # ax.set_title("Time spent working today", va='bottom')
        # ax.bar(x=0, height=time/(self.objective*3600), width=2*np.pi, color='green')
        # base styling logic
        ring_width = 0.3
        outer_radius = 1.5
        inner_radius = outer_radius - ring_width

        # set up plot
        value = time/3600
        ring_arrays = calculate_rings(value, self.objective)
        fig, ax = plt.subplots()

        if value > self.objective:
            ring_to_label = 0
            outer_edge_color = None
            inner_edge_color = self.fg_string
        else:
            ring_to_label = 1
            outer_edge_color, inner_edge_color = [self.fg_string, None]

        # plot logic
        try:
            outer_ring, _ = ax.pie(ring_arrays[0], radius=1.5,
                                colors=[self.colormap[-1], self.colormap[0]],
                                startangle = 90,
                                counterclock = False)
            plt.setp( outer_ring, width=ring_width, edgecolor=outer_edge_color)
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
        # plt.show()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.canvas.get_tk_widget().config(bg=self.bg_string)
        self.canvas.draw()
        self.window.update()

def calculate_rings(value, objective):
    #USE: Create an array structure for rings.
    #INPUT: a df of row length 1 with the first column as the current metric value and the second colum is the target metric value
    #OUTPUT: an aray of arrays representing each ring
    if value < objective:
        rings=[[value,objective-value],[0,0]]
    elif value / objective < 2:
        rings=[[value,0],[value % objective, objective-value % objective]]
    else:
        rings = [[0,0],[0,0]]
    return rings

def horizontal_aligner(value, objective):
    #USE: Determine if the label for the rotating number label should be left/center/right
    #INPUT: a df of row length 1 with the first column as the current metric value and the second colum is the target metric value
    #OUTPUT: the proper text alignment
    metric = 1.0 * value % objective / objective
    if metric in (0, 0.5):
        align = 'center'
    elif metric < 0.5:
        align = 'left'
    else:
        align = 'right'
    return align

def vertical_aligner(value, objective):
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


#USE: Create a center label in the middle of the radial chart.
#INPUT: a df of row length 1 with the first column as the current metric value and the second column is the target metric value
#OUTPUT: the proper text label
def add_center_label(value, objective, color):
    percent = str(round(1.0*value/objective*100,1)) + '%'
    return plt.text(0,
           0.2,
           percent,
           horizontalalignment='center',
           verticalalignment='center',
           fontsize = 40,
           color=color,
           family = 'sans-serif')

#USE: Create a dynamic outer label that servers a pointer on the ring.
#INPUT: a df of row length 1 with the first column as the current metric value and the second column is the target metric value
#OUTPUT: the proper text label at the apropiate position
def add_current_label(value, objective, color):
    # print('vertical: ' + vertical_aligner(value, objective))
    # print('horizontal: ' + horizontal_aligner(value, objective))
    return plt.text(1.5 * np.cos(0.5 *np.pi - 2 * np.pi * (float(value) % objective /objective)),
            1.5 * np.sin(0.5 *np.pi - 2 * np.pi * (float(value) % objective / objective)),
                    str(round(value, 2)),
                    horizontalalignment=horizontal_aligner(value, objective),
                    verticalalignment=vertical_aligner(value, objective),
                    fontsize = 20,
                    color=color,
                    family = 'sans-serif')

def add_sub_center_label(objective, color):
    amount = 'Goal: ' + str(objective) + 'h'
    return plt.text(0,
            -.1,
            amount,
            color=color,
            horizontalalignment='center',
            verticalalignment='top',
            fontsize = 22,family = 'sans-serif')
