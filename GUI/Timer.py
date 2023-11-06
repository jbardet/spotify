import time
import tkinter as tk
from tkinter import StringVar, Entry, Label, Button
from tkinter import messagebox
from helpers import add_website_link
import numpy as np
import pandas as pd
import requests
import json
from io import StringIO
from Calendar import Calendar
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pygsheets
import pandas as pd

class Timer():
    """
    Class to handle the POMODORO timer but also the links to the stretching
    websites
    """
    def __init__(self, window: tk.Frame, objective: float) -> None:
        """
        Initialize the frame with the timer and the links

        :param window: the window frame where to place the timer and the links
        :type window: tk.Frame
        """
        self.window = window
        self.add_timer()
        self.sec = np.inf
        self.run = False
        self.objective = objective

        # Create empty dataframe
        self.timer_dict = {"event": [],
                           "time": []}

        self.offline_dict = {
            'category': [],
            'description': [],
            'start': [],
            'end': []
        }
        total_time = self.compute_time()
        self.add_radial_plot(total_time)

    def compute_time(self):
        # gather the sum of the time for all offline_dict entries
        offline_time = np.sum([(datetime.strptime(self.offline_dict['end'][i], "%H:%M") - datetime.strptime(self.offline_dict['start'][i], "%H:%M")).seconds for i in range(len(self.offline_dict['start']))])
        timer_time = 0
        for i, event in enumerate(self.timer_dict['event']):
            if i == 0: continue
            if self.timer_dict['event'][i-1] == "start" and (event == 'pause' or event == 'stop'):
                timer_time += (self.timer_dict['time'][i] - self.timer_dict['time'][i-1]).total_seconds()
        return offline_time + timer_time

    def play(self):
        self.timer_dict['event'].append("start")
        self.timer_dict['time'].append(datetime.now())
        self.run = True
        self.submit()

    def submit(self):
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
            if not self.run:
                return
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
                label = tk.Label(toplevel,
                                 text="Time's up. Take a break, here are some stretching links:",
                                 font=("Arial",18,""))
                label.pack(side=tk.TOP)
                self.add_links(toplevel)
                self.reset()

            # after every one sec the value of temp will be decremented
            # by one
            self.sec -= 1

    def pause(self):
        """
        Pause the timer
        """
        self.timer_dict['event'].append("pause")
        self.timer_dict['time'].append(datetime.now())
        self.run = False

    def stop(self):
        """
        Stop the timer
        """
        self.timer_dict['event'].append("stop")
        self.timer_dict['time'].append(datetime.now())
        self.reset()
        total_time = self.compute_time()
        self.add_radial_plot(total_time)

    def reset(self):
        self.hour.set("00")
        self.minute.set("50")
        self.second.set("00")

    def add_timer(self) -> None:
        """
        Add a timer in the upper right part of the GUI
        """
        # Declaration of variables
        self.hour=StringVar()
        self.minute=StringVar()
        self.second=StringVar()

        # Setting the default value as 50 minutes (preferred time for a pomodoro)
        self.reset()

        # # Set a label to explain the timer
        # timer_label = Label(self.window, text="POMODORO: ", font=("Arial",18,""))
        # timer_label.pack(side = tk.TOP)

        # Use of Entry class to take input from the user
        hourEntry= Entry(self.window, width=3, font=("Arial",18,""),
                         textvariable=self.hour)
        # place it in upper right corner
        hourEntry.pack(side = tk.LEFT)

        minuteEntry= Entry(self.window, width=3, font=("Arial",18,""),
                           textvariable=self.minute)
        minuteEntry.pack(side = tk.LEFT)

        secondEntry= Entry(self.window, width=3, font=("Arial",18,""),
                           textvariable=self.second)
        secondEntry.pack(side = tk.LEFT)

        # Button widget to start the countdown
        btn = Button(self.window, text='Start', font=("Arial",18),
                    command= self.play)
        btn.pack(side = tk.LEFT)
        btn = Button(self.window, text='Pause', font=("Arial",18),
                    command= self.pause)
        btn.pack(side = tk.LEFT)
        btn = Button(self.window, text='Stop', font=("Arial",18),
                    command= self.stop)
        btn.pack(side = tk.LEFT)

        enter_offline = tk.Button(self.window, text="Enter", font=("Arial",18),
                                  command= self.enter_offline_work)
        enter_offline.pack(side = tk.BOTTOM)

        self.end = Entry(self.window, width = 20)
        self.end.bind("<Button-1>", lambda e: self.end.delete(0, tk.END))
        self.end.insert(0,'end')
        self.end.pack(side = tk.BOTTOM)
        self.start = Entry(self.window, width = 20)
        self.start.bind("<Button-1>", lambda e: self.start.delete(0, tk.END))
        self.start.insert(0,'start')
        self.start.pack(side = tk.BOTTOM)

        self.description = Entry(self.window, width = 50)
        self.description.bind("<Button-1>", lambda e: self.description.delete(0, tk.END))
        self.description.insert(0,'Description')
        self.description.pack(side = tk.BOTTOM)

        self.category = Entry(self.window, width = 20)
        self.category.bind("<Button-1>", lambda e: self.category.delete(0, tk.END))
        self.category.insert(0,'Category')
        self.category.pack(side = tk.BOTTOM)

        offline_label = tk.Label(self.window, text="Enter offline work: ", font=("Arial",18))
        offline_label.pack(side = tk.BOTTOM)

    def add_links(self, window: tk.Frame) -> None:
        """
        Add links to the stretching websites on the GUI
        """

        texts = ["healthline", "verywellfit"]
        urls = [
            "https://www.healthline.com/health/deskercise",
            "https://www.verywellfit.com/best-stretches-for-office-workers-1231153"
        ]
        font = ('Aerial 12')
        side = "bottom"

        add_website_link(window, urls[0], texts[0], font, side)
        add_website_link(window, urls[1], texts[1], font, side)

    def enter_offline_work(self):
        self.offline_dict['category'].append(self.category.get())
        self.offline_dict['description'].append(self.description.get())
        self.offline_dict['start'].append(self.start.get())
        self.offline_dict['end'].append(self.end.get())
        total_time = self.compute_time()
        self.add_radial_plot(total_time)

    def save_data(self):
        # authorization
        gc = pygsheets.authorize(service_file='creditentials/spotify-402405-59d8f4e06e41.json')
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        # DO NOT FORGET TO SHARE THE SPREADSHEET
        sh = gc.open('timer_data.csv')

        #select the first sheet
        wks = sh[0]

        # existing df
        df_drive = wks.get_as_df()

        #update the first sheet with df, starting at cell B2.
        df = pd.DataFrame.from_dict(self.timer_dict)
        df_save = pd.concat([df_drive, df], ignore_index=True)
        wks.set_dataframe(df_save,(0,0))


        sh = gc.open('offline_work.csv')
        #select the first sheet
        wks = sh[0]

        # existing df
        df_drive = wks.get_as_df()

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
        color_theme = 'Purple'
        color = plt.get_cmap(color_theme + 's')
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
            inner_edge_color = 'white'
        else:
            ring_to_label = 1
            outer_edge_color, inner_edge_color = ['white', None]

        # plot logic
        outer_ring, _ = ax.pie(ring_arrays[0],radius=1.5,
                            colors=[color(0.9), color(0.15)],
                            startangle = 90,
                            counterclock = False)
        plt.setp( outer_ring, width=ring_width, edgecolor=outer_edge_color)
        try:
            inner_ring, _ = ax.pie(ring_arrays[1],
                                    radius=inner_radius,
                                    colors=[color(0.55), color(0.05)],
                                    startangle = 90,
                                    counterclock = False)
            plt.setp(inner_ring, width=ring_width, edgecolor=inner_edge_color)
        except ValueError:
            pass

        # add labels and format plots
        add_center_label(value, self.objective)
        add_current_label(value, self.objective)
        add_sub_center_label(self.objective)
        ax.axis('equal')
        plt.margins(0,0)
        plt.autoscale('enable')
        # plt.show()
        self.canvas = FigureCanvasTkAgg(fig, master=self.window)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
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
def add_center_label(value, objective):
    percent = str(round(1.0*value/objective*100,1)) + '%'
    return plt.text(0,
           0.2,
           percent,
           horizontalalignment='center',
           verticalalignment='center',
           fontsize = 40,
           family = 'sans-serif')

#USE: Create a dynamic outer label that servers a pointer on the ring.
#INPUT: a df of row length 1 with the first column as the current metric value and the second column is the target metric value
#OUTPUT: the proper text label at the apropiate position
def add_current_label(value, objective):
    print('vertical: ' + vertical_aligner(value, objective))
    print('horizontal: ' + horizontal_aligner(value, objective))
    return plt.text(1.5 * np.cos(0.5 *np.pi - 2 * np.pi * (float(value) % objective /objective)),
            1.5 * np.sin(0.5 *np.pi - 2 * np.pi * (float(value) % objective / objective)),
                    str(round(value, 2)),
                    horizontalalignment=horizontal_aligner(value, objective),
                    verticalalignment=vertical_aligner(value, objective),
                    fontsize = 20,
                    family = 'sans-serif')

def add_sub_center_label(objective):
    amount = 'Goal: ' + str(objective) + 'h'
    return plt.text(0,
            -.1,
            amount,
            horizontalalignment='center',
            verticalalignment='top',
            fontsize = 22,family = 'sans-serif')


