import numpy as np
import tkinter as tk
from typing import List
import pickle
import requests
from colour import Color
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import requests
import matplotlib.pyplot as plt

from helpers import add_website_link

# TODO: change date in the API calls to today's date from last week? or only today?
# TODO: add a connection to a database to save results (or on disk might be easier)

class RescueTime():
    """
    Integrate a Rescue time window to see your daily activity
    """
    def __init__(self, key:str, window: tk.Frame) -> None:
        """
        Initialize the RescueTime class from the API key and the GUI window
        where to place it

        :param key: the user key to access the API
        :type key: str
        :param window: the window where to place the RescueTime widget
        :type window: tk.Frame
        """
        self.__key = key
        self.window = window

        self.start_call = f"https://www.rescuetime.com/anapi/start_focustime?key={self.__key}&duration=-1"
        self.end_call = f"https://www.rescuetime.com/anapi/end_focustime?key={self.__key}"
        self.rescue_time_is_on = False # self.is_rescue_time_on()

        self.rank_call = f"https://www.rescuetime.com/anapi/data?key={self.__key}&perspective=rank&restrict_kind=productivity&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"
        self.category_call = f"https://www.rescuetime.com/anapi/data?key={self.__key}&perspective=rank&restrict_kind=document&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"

        self.color_palette = self.create_color_palette()

    def is_rescue_time_on(self) -> bool:
        """
        Make a request to the API to see if the RescueTime app is on already
        and stop it otherwise

        :return: False because if RescueTime is on, we want to stop it
        :rtype: bool
        """
        requests.get(self.end_call)
        return False

    def create_color_palette(self) -> List[Color]:
        """
        Create a color palette from green (productive) to red (distracting)

        :return: a list of colors
        :rtype: List[Color]
        """
        red = Color("green")
        colors = list(red.range_to(Color("red"),5))
        colors = [col.hex for col in colors]
        return colors

    def add_analytics(self) -> None:
        """
        Add RescueTime analytics to the left part of the main GUI

        We add:
        - a link to RescueTime's website to have a more in-depth analysis and
            add offline times
        - a horizontal bar chart of the productivity rank [-2,2]
        - a vertical bar chart with category and productivity (color)
        - a button to turn on/off RescueTime when going on a break
        """

        self.add_website_link()

        # TODO: Also add a button either to oy.system to open RescueTime app
        # to add offline work or make a widget to add offline work

        self.add_analytics_plots()
        self.add_start_rescue_time_button()

    def add_website_link(self) -> None:
        """
        Add a label to access the RescueTime website for analytics
        """
        text = "RescueTime"
        font= ('Aerial 12')
        side = "top"
        url = "https://www.rescuetime.com/rtx/reports/activities"
        add_website_link(self.window, url, text, font, side)

    def add_analytics_plots(self) -> None:
        """
        Make the analytics plots for some motivation and add to the GUI
        """
        self.add_ranked_plot()
        self.add_categorical_plot()

    def add_ranked_plot(self) -> None:
        """
        Make the ranked plot and add to the GUI
        """
        # # Get the ranked data from the API
        # response = requests.get(self.rank_call)
        # data_rank = response.json()
        # with open("data_prod_rank.pickle", "wb") as file:
        #     pickle.dump(data_rank, file)
        with open('data_prod_rank.pickle', 'rb') as handle:
            data_rank = pickle.load(handle)

        # Make a horizontal bar chart with the productivity score [-2,2] and
        # the time spent in hours
        rows = data_rank['rows']
        data_to_plot = [[] for _ in range(len(rows))]
        for row in data_rank['rows']:
            data_to_plot[2-row[-1]] = [row[-1], row[1]]

        # Make the plot and add it to the GUI window
        fig, (self.ax) = plt.subplots(1, 1, figsize=(5,2))
        plt.title("Productivity Rank (2 most productive, -2 most distracting))")
        plt.xlabel("Time (hours)")
        plt.barh(np.array(data_to_plot)[:,0],
                 np.array(data_to_plot)[:,1]/3600,
                 color=self.color_palette)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side = tk.TOP)

    def add_categorical_plot(self) -> None:
        """
        Make the categorical plot and add to the GUI
        """
        # # Get the categorical data from the API
        # response = requests.get(self.category_call)
        # data_cat = response.json()
        # with open("data6.pickle", "wb") as file:
        #     pickle.dump(data_cat, file)
        with open('data6.pickle', 'rb') as handle:
            data_cat = pickle.load(handle)

        # Make a vertical bar chart with the category and productivity score
        df = pd.DataFrame(data_cat['rows'],
                          columns = ['rank', 'time', 'people', 'activity',
                                     'document', 'category', 'productivity'])
        # Sort the Serie by value and only show the 10 biggest categories on the plot
        top_ten = df.groupby("category").sum()['time'].sort_values(ascending=False)[:10]
        plot_colors = [self.color_palette[2-df[df['category'] ==cat]['productivity'].iloc[0]]
                       for cat in top_ten.keys()]

        # Make the plot and add it to the GUI window
        fig, (self.ax) = plt.subplots(1, 1, figsize=(5,4))
        plt.title("Categories")
        plt.ylabel("Time (hours)")
        plt.bar(top_ten.keys(), top_ten.values/3600, color=plot_colors)
        # Add angle to the labels to see all labels entirely
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side = tk.TOP)

    def add_start_rescue_time_button(self) -> None:
        """
        Add a button to Start/End rescue time depending on whether RescueTime
        is already on or not
        """

        def start_rescue_time() -> None:
            """
            Start the RescueTime app and change text in the button when clicked
            """
            if self.rescue_time_is_on:
                call = self.end_call
                self.rescue_time_is_on = True
                self.rescue_time_button.configure(text = "End RescueTime")
            else:
                call = self.end_call
                self.rescue_time_is_on = False
                self.rescue_time_button.configure(text = "Start RescueTime")
            response = requests.get(call)
            if response.status_code == 404:
                print("rescue_time_is_on is wrong ")

        # Add the button to the GUI window
        text = "End RescueTime" if self.rescue_time_is_on else "Start RescueTime"
        self.rescue_time_button = tk.Button(self.window, text = text,
                                            command = start_rescue_time)
        self.rescue_time_button.pack(side = tk.TOP)

# # for the analytic data:
# # perspective -> rank or interval
# # resolution_time -> [ 'month' | 'week' | 'day' | 'hour' | 'minute' ]
# # restrict_begin
# # restrict_end
# # restrict_kind -> [ 'category' | 'activity' | 'productivity' | 'document' ]
# # restrict_thing -> name (of category, activity, or overview)
# # restrict_thingy
# # restrict_source_type -> [ 'computers' | 'mobile' | 'offline' ]
# # restrict_schedule_id -> id (integer id of user's schedule/time filter)
# productivity_call = f"https://www.rescuetime.com/anapi/data?key={self.__key}&perspective=interval&restrict_kind=productivity&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"
# overview_call = f"https://www.rescuetime.com/anapi/data?key={self.__key}&perspective=rank&restrict_kind=overview&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"

# # Daily summary feed
# daily_summary = f"https://www.rescuetime.com/anapi/daily_summary_feed?key={self.__key}"

# # Alerts feed api Alerts are a premium feature and as such the API will always return zero results for users on the RescueTime Lite plan.
# # Highlights also premium, FocusTime Feed API also
# # alert_call = f"https://www.rescuetime.com/anapi/alerts_feed?key={self.__key}&op=list"

# # FocusTime Trigger API -> start/end FocusTime on active devices as an alternative to starting/ending it manually from the desktop app.
# # duration is in min and -1 if until end of the day (return 200 if ok, 400 if fails)
# start_call = f"https://www.rescuetime.com/anapi/start_focustime?key={self.__key}&duration=30"
# end_call = f"https://www.rescuetime.com/anapi/end_focustime?key={self.__key}"

# # Offline Time POST API -> add offline time to a user's account (200/400), t in minutes, detail is optional
# offline_call = f"https://www.rescuetime.com/anapi/offline_time_post?key={self.__key}"
# offline_json = {
#     "start_time": "2020-01-01 09:00:00",
#     "duration": 60,
#     "activity_name": "Meeting",
#     "activity_details": "Daily Planning"
#     }
