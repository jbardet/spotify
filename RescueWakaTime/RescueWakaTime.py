import numpy as np
import tkinter as tk
from typing import List
import pickle
import requests
import sys
import hashlib
import os
import json
import datetime
import pickle
# from colour import Color
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import requests
import matplotlib.pyplot as plt
from rauth import OAuth2Service
from urllib.parse import parse_qsl
from datetime import timedelta as td
import tkinter.ttk as ttk
import matplotlib

from Helpers.helpers import add_website_link, set_plot_color
from Credentials.Credentials import Credentials
from Configs.Parser import Parser

class RescueWakaTime():
    """
    Integrate a Rescue time window to see your daily activity
    """

    def __init__(self):
        """
        Initialize the RescueTime class from the API key
        """
        self.__rescue_key = Credentials.get_rescuetime_credentials()
        self.__waka_key = Credentials.get_wakatime_credentials()
        today = datetime.date.today()
        self.today = f"{today.year}-{today.month}-{today.day}"

        if len(self.__rescue_key) == 0:
            print("Warning, RescueTime credentials not found, will skip it")
            self.data_activity = {}
        else:
            self.start_call = f"https://www.rescuetime.com/anapi/start_focustime?key={self.__rescue_key}&duration=-1"
            self.end_call = f"https://www.rescuetime.com/anapi/end_focustime?key={self.__rescue_key}"
            self.rank_call = f"https://www.rescuetime.com/anapi/data?key={self.__rescue_key}&perspective=rank&restrict_kind=productivity&interval=hour&restrict_begin={self.today}&restrict_end={self.today}&format=json"
            self.category_call = f"https://www.rescuetime.com/anapi/data?key={self.__rescue_key}&perspective=rank&restrict_kind=document&interval=hour&restrict_begin={self.today}&restrict_end={self.today}&format=json"
            self.activity_call = f"https://www.rescuetime.com/anapi/data?key={self.__rescue_key}&perspective=rank&restrict_kind=activity&interval=hour&restrict_begin={self.today}&restrict_end={self.today}&format=json"
            self.data_activity = self.get_data_activity()

        if len(self.__waka_key) == 0:
            print("Warning, WakaTime credentials not found, will skip it")
        else:
            self.status_call = "https://wakatime.com/api/v1/users/current/status_bar/today?api_key="+self.__waka_key
            self.status_bar = self.get_status_bar()

    def get_status_bar(self) -> dict:
        """
        Get the status bar from WakaTime

        :return: the result from the API
        :rtype: _type_
        """
        response = requests.get(self.status_call)
        try:
            return response.json()
        except json.decoder.JSONDecodeError as e :
            return {}

    def get_data_activity(self) -> dict:
        """
        Get the status bar from RescueTime

        :return: the result from the API
        :rtype: dict
        """
        response = requests.get(self.activity_call)
        return response.json()

    def update_analytics(self):
        """
        Update the plots on the GUI based on daily advances
        """
        self.data_activity = self.get_data_activity()
        self.status_bar = self.get_status_bar()
        for widget in self.window.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass
        self.add_analytics()

    def build_frame(self, window: ttk.Frame, bg_string: str, fg_string: str):
        """
        Build the frame for the RescueTime window

        :param window: the Frame of the Window
        :type window: ttk.Frame
        :param bg_string: the background color
        :type bg_string: str
        :param fg_string: the foreground color
        :type fg_string: str
        """
        self.window = window
        self.bg_string = bg_string
        self.fg_string = fg_string
        self.color_theme = Parser.get_plt_theme()
        self.color_palette = plt.get_cmap(self.color_theme)(np.linspace(0, 1, 7))[1:-1]
        self.color_palette = np.flip(self.color_palette, 0)
        self.bigfigsize = (5, 4)
        self.smallfigsize = (5, 2)

    def add_analytics(self):
        """
        Add RescueTime analytics to the left part of the main GUI

        We add:
        - a link to RescueTime's website to have a more in-depth analysis and
            add offline times
        - a horizontal bar chart of the productivity rank [-2,2]
        - a vertical bar chart with category and productivity (color)
        """

        link_frame = ttk.Frame(self.window)
        link_frame.pack(side='top', anchor='c', fill='both', expand=True)

        text = "RescueTime"
        url = "https://www.rescuetime.com/rtx/reports/activities"
        side = "left"
        self.add_website_link(link_frame, text, url, side)

        text = "Wakatime"
        url = "https://wakatime.com/dashboard"
        side = "right"
        self.add_website_link(link_frame, text, url, side)

        # TODO: Also add a button either to oy.system to open RescueTime app
        # to add offline work or make a widget to add offline work

        self.add_analytics_plots()
        # self.add_start_rescue_time_button()

    def add_website_link(self, window: ttk.Frame, text: str, url: str, side: str):
        """
        Add a label to access the RescueTime website for analytics

        :param window: the frame to place the links
        :type window: ttk.Frame
        :param text: the text to display
        :type text: str
        :param url: the link to be clicked
        :type url: str
        :param side: the side to place the label
        :type side: str
        """
        font = ('Aerial', '16', 'underline')
        add_website_link(window, url, text, font, side, fg=self.fg_string, bg=self.bg_string)

    def add_analytics_plots(self) -> None:
        """
        Make the analytics plots for some motivation and add to the GUI
        """
        # self.data_activity['row_headers'] are:
        #  ['Rank', 'Time Spent (seconds)', 'Number of People', 'Activity', 'Category', 'Productivity']
        columns = ['rank', 'time', 'people', 'activity', 'category', 'productivity']
        try:
            df = pd.DataFrame(self.data_activity['rows'], columns = columns)
        except KeyError:
            df = pd.DataFrame(self.data_activity, columns = columns)
        # Add the plots based on the activites
        self.add_ranked_plot(df.groupby("productivity").sum()['time'])
        self.add_categorical_plot(df)
        # if we don't provide a WakaTime key, it means we don't want to connect to
        # WakaTime, thus we only plot RescueTime data
        if len(self.__waka_key) == 0:
            self.add_activity_plot(df)
        else:
            self.add_wakatime_plot(df)

    def add_wakatime_plot(self, df: pd.DataFrame):
        """
        Adds the WakaTime plot to the Frame

        :param df: the DataFrame with RescueTime's data
        :type df: pd.DataFrame
        """
        # status bar: ['grand_total', 'range', 'projects', 'languages',
        # 'dependencies', 'machines', 'editors', 'operating_systems', 'categories']

        # here rt means RescueTime, wt WakaTime
        rt_tot_time = df['time'].sum()/3600
        try:
            rt_prod_time = df.groupby('productivity').sum()['time'][2]/3600
        except (IndexError, KeyError) as e:
            print(e)
            rt_prod_time = 0
        try:
            rt_vs_time = df.groupby('activity').sum()['time']['Visual Studio Code']/3600
        except (IndexError, KeyError) as e:
            print(e)
            rt_vs_time = 0
        try:
            total_today = self.status_bar['data']['grand_total']['decimal']
            categories = self.status_bar['data']['categories']
        except (IndexError, KeyError) as e:
            print(e)
            total_today = 0
            categories = []
        if isinstance(total_today, str):
            total_today = 0
            categories = []
        # Make the plot and add it to the GUI window
        self.create_barplot(["RT_tot", "RT_prod", "RT_VS", "WT_tot"] + [cat['name'] for cat in categories],
                            [rt_tot_time, rt_prod_time, rt_vs_time,
                            float(total_today)] + [float(cat['decimal']) for cat in categories],
                            plt.get_cmap(self.color_theme)(np.linspace(0, 1, 8))[1:-1],
                            title="Time analysis",
                            ylabel="Time (hours)")

    def create_barplot(self,
                       labels: List[str],
                       values: List[float],
                       colors: List[str],
                       title: str,
                       ylabel: str):
        """
        Creates the vertical barplots for RescueTime's different datas

        :param labels: the labels to display on the x-axis
        :type labels: List[str]
        :param values: the values of the different bars
        :type values: List[float]
        :param colors: the colors of the bars based on productivity levels
        :type colors: List[str]
        :param title: the title of the graph
        :type title: str
        :param ylabel: the label of the y-axis
        :type ylabel: str
        """
        fig, (ax) = plt.subplots(1, 1, figsize=self.bigfigsize)
        plt.title(title)
        plt.ylabel(ylabel)
        plt.bar(labels, values, color=colors)
        # Add angle to the labels to see all labels entirely
        plt.xticks(rotation=45, ha='right')
        self.create_plot(fig, ax)

    def create_plot(self, fig: matplotlib.figure, ax: matplotlib.axes.Axes):
        """
        Creates a Canvas from a matplotlib figure and axis object

        :param fig: the figure to display
        :type fig: matplotlib.figure
        :param ax: the axes of the figure to display
        :type ax: matplotlib.axes.Axes
        """
        plt.tight_layout()
        fig, ax = set_plot_color(fig, ax, self.fg_string)
        canvas = FigureCanvasTkAgg(fig, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas.get_tk_widget().config(bg=self.bg_string)
        canvas_widget.pack(side = tk.TOP)

    def add_activity_plot(self, df: pd.DataFrame):
        """
        Adds an Activity plot based on RescueTime's activities

        :param df: RescueTime's activities
        :type df: pd.DataFrame
        """
        # Make a vertical bar chart with the category and productivity score
        # Sort the Serie by value and only show the 10 biggest categories on the plot
        top_ten = df.groupby("activity").sum()['time'].sort_values(ascending=False)[:10]
        plot_colors = [self.color_palette[2-df[df['activity'] ==cat]['productivity'].iloc[0]]
                       for cat in top_ten.keys()]

        # Make the plot and add it to the GUI window
        self.create_barplot(get_labels(top_ten.keys(), 18),
                            top_ten.values/3600,
                            plot_colors,
                            title="Activities",
                            ylabel="Time (hours)")

    def add_ranked_plot(self, rank: pd.Series):
        """
        Make the ranked plot and add to the GUI

        :param rank: _description_
        :type rank: pd.Series
        """

        # Make a horizontal bar chart with the productivity score [-2,2] and
        # the time spent in hours
        data_to_plot = [[] for _ in range(5)]
        for key, value in rank.items():
            data_to_plot[2-key] = [key, value]
        for i, sublist in enumerate(data_to_plot):
            if len(sublist)<2:
                data_to_plot[i] = [2-i, 0]

        # Make the plot and add it to the GUI window
        fig, (ax) = plt.subplots(1, 1, figsize=self.smallfigsize)
        plt.title("Productivity (2 most productive, -2 most distracting))")
        plt.xlabel("Time (hours)")
        plt.barh(np.array(data_to_plot)[:,0],
                np.array(data_to_plot)[:,1]/3600,
                color=self.color_palette)
        self.create_plot(fig, ax)

    def add_categorical_plot(self, df: pd.DataFrame) -> None:
        """
        Make the categorical plot about RescueTime's categories of work and add
        to the GUI

        :param df: the DataFrame with RescueTime's data
        :type df: pd.DataFrame
        """

        # # Make a vertical bar chart with the category and productivity score
        # # Sort the Serie by value and only show the 10 biggest categories on the plot
        top_ten = df.groupby("category").sum()['time'].sort_values(ascending=False)[:10]
        plot_colors = [self.color_palette[2-df[df['category'] ==cat]['productivity'].iloc[0]]
                       for cat in top_ten.keys()]

        # Make the plot and add it to the GUI window
        self.create_barplot(get_labels(top_ten.keys(), 18),
                            top_ten.values/3600,
                            [self.color_palette[2-df[df['category'] ==cat]['productivity'].iloc[0]]
                             for cat in top_ten.keys()],
                            "Categories",
                            "Time (hours)")

    def save_data(self, __backup_path):
        """
        Save the weekly data from the API in a json file
        """
        # get the last save from the last csv file
        # activities_saved = pd.read_csv('data/first_save/rescuetime_activities.csv')
        # activities_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
        # activities_saved.drop_duplicates(subset = ["date","time","activity","category","document","productivity","device"], inplace = True)
        # activities_saved.to_csv('data/first_save/rescuetime_activities.csv')
        # activities_saved = pd.read_csv('data/first_save/rescuetime_overview.csv')
        # activities_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
        # activities_saved.drop_duplicates(subset = ["date","time","category","device"], inplace = True)
        # activities_saved.to_csv('data/first_save/rescuetime_overview.csv')
        # print("oe")
        try:
            activities_saved = pd.read_csv(os.path.join(__backup_path, 'rescuetime_activities.csv'))
            activities_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            # activities_saved.sort_values(by='date', inplace=True)
            # activities_saved.to_csv('data/rescuetime_activities.csv')
            activities_last_save = activities_saved['date'].iloc[-1]
            summary_saved = pd.read_csv(os.path.join(__backup_path, 'rescuetime_summary.csv'))
            summary_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            # summary_saved.sort_values(by='date', inplace=True)
            # summary_saved.to_csv('data/rescuetime_summary.csv')
            summary_last_save = activities_saved['date'].iloc[-1]
            overview_saved = pd.read_csv(os.path.join(__backup_path, 'rescuetime_overview.csv'))
            overview_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            # overview_saved.sort_values(by='date', inplace=True)
            # overview_saved.to_csv('data/rescuetime_overview.csv')
            overview_last_save = overview_saved['date'].iloc[-1]
        except FileNotFoundError:
            activities_last_save = '2023-10-10 06:00:00'
            summary_last_save = '2023-10-10'
            overview_last_save = '2023-10-10 06:00:00'
        activities_date_save = datetime.datetime.strptime(activities_last_save.split(" ")[0], '%Y-%m-%d').date().strftime('%Y-%m-%d')
        overview_date_save = datetime.datetime.strptime(overview_last_save.split(" ")[0], '%Y-%m-%d').date().strftime('%Y-%m-%d')
        summary_date_save = datetime.datetime.strptime(summary_last_save.split(" ")[0], '%Y-%m-%d').date().strftime('%Y-%m-%d')
        restrict_source_types = ['computers', 'mobile', 'offline']
        today = datetime.date.today()
        # today = datetime.datetime.strptime('2023-10-20', '%Y-%m-%d').date()
        activities_dict = {
            'date': [],
            'time': [],
            'activity': [],
            'category': [],
            'document': [],
            'productivity': [],
            'device': []
        }
        overview_dict = {
            'date': [],
            'time': [],
            'category': [],
            'device': []
        }

        # RescueTime
        baseurl = 'https://www.rescuetime.com/anapi/data?key='
        url = baseurl+self.__rescue_key

        for restrict_source_type in restrict_source_types:
            # Configuration for Query
            payload = {
                'perspective':'interval',
                'resolution_time': 'minute', #1 of "month", "week", "day", "hour", "minute"
                'restrict_kind': 'document', # 'document', 'activity'
                'restrict_begin': activities_date_save,
                'restrict_end': today,
                'format':'json', #csv
                'restrict_source_type': restrict_source_type
            }

            # Setup Iteration - by Day
            d1 = datetime.datetime.strptime(payload['restrict_begin'], "%Y-%m-%d").date()
            d2 = payload['restrict_end']
            delta = d2 - d1

            # Iterate through the days, making a request per day
            for i in range(delta.days + 1):
                # Find iter date and set begin and end values to this to extract at once.
                d3 = d1 + td(days=i) # Add a day
                if d3.day == 1: print('Pulling Monthly Data for ', d3)

                # Update the Payload
                payload['restrict_begin'] = str(d3) # Set payload days to current
                payload['restrict_end'] = str(d3)   # Set payload days to current

                # Request
                try:
                    r = requests.get(url, payload) # Make Request
                    iter_result = r.json() # Parse result
                    # print("Collecting Activities for " + str(d3))
                except Exception as e:
                    print(e)
                    print("Error collecting data for " + str(d3))

                if len(iter_result) != 0:
                    for i in iter_result['rows']:
                        activities_dict['date'].append(datetime.datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%S"))
                        activities_dict['time'].append(i[1])
                        activities_dict['activity'].append(i[3])
                        activities_dict['document'].append(i[4])
                        activities_dict['category'].append(i[5])
                        activities_dict['productivity'].append(i[6])
                        activities_dict['device'].append(restrict_source_type)
                else:
                    print("Appears there is no RescueTime data for " + str(d3))

            # Setup Iteration - by Day for overview
            d1 = datetime.datetime.strptime(overview_date_save, "%Y-%m-%d").date()
            d2 = today
            delta = d2 - d1

            # Iterate through the days, making a request per day
            for i in range(delta.days + 1):
                # Find iter date and set begin and end values to this to extract at once.
                d3 = d1 + td(days=i) # Add a day
                # Request
                try:
                    overview_call = f"https://www.rescuetime.com/anapi/data?key={self.__rescue_key}&perspective=interval&restrict_kind=overview&restrict_begin={str(d3)}&restrict_end={str(d3)}&resolution=minute&format=json&restrict_source_type={restrict_source_type}"
                    overview = requests.get(overview_call).json()
                    # print("Collecting Activities for " + str(d3))
                except Exception as e:
                    print(e)
                    print("Error collecting data for " + str(d3))

                if len(overview) != 0:
                    for i in overview['rows']:
                        overview_dict['date'].append(datetime.datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%S"))
                        overview_dict['time'].append(i[1])
                        overview_dict['category'].append(i[3])
                        overview_dict['device'].append(restrict_source_type)
                else:
                    print("Appears there is no RescueTime data for " + str(d3))

        overview_added = pd.DataFrame.from_dict(overview_dict)
        activities_added = pd.DataFrame.from_dict(activities_dict)
        # overview_added = pd.read_csv('data/rescuetime_overview_added.csv')
        # overview_added.drop(['Unnamed: 0'], axis=1, inplace=True)
        # activities_added = pd.read_csv('data/rescuetime_activities_added.csv')
        # activities_added.drop(['Unnamed: 0'], axis=1, inplace=True)
        overview_added.sort_values(by='date', inplace=True)
        activities_added.sort_values(by='date', inplace=True)
        # append the loaded dataframe with the one we just created
        overview_added_copy = overview_added.copy()
        for i, row in overview_added.iterrows():
            # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
            # otherwise not
            # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
            if row['date']<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                # remove the row
                overview_added_copy.drop(i, inplace=True)
            # elif datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")==datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
            elif row['date']==datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                len_overview = len(overview_saved)
                overview_saved.drop(overview_saved[
                    (overview_saved['date'] == overview_last_save) &
                    (overview_saved['category'] == row['category']) &
                    (overview_saved['device'] == row['device'])].index, inplace=True)
                # assert len_overview-len(overview_saved) == 1
        overview_added = overview_added_copy
        activities_added_copy = activities_added.copy()
        for i, row in activities_added.iterrows():
            # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
            # otherwise not
            # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S") < datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
            if row['date'] < datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
                # remove the row
                activities_added_copy.drop(i, inplace=True)
            # elif datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")==datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
            elif row['date']==datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
                # len_activities = len(activities_saved)
                activities_saved.drop(activities_saved[
                    (activities_saved['date'] == activities_last_save) &
                    (activities_saved['activity'] == row['activity']) &
                    (activities_saved['category'] == row['category']) &
                    (activities_saved['document'] == row['document']) &
                    (activities_saved['productivity'] == row['productivity']) &
                    (activities_saved['device'] == row['device'])].index, inplace=True)
                # assert len_activities-len(activities_saved) == 1
        activities_added = activities_added_copy
        try:
            overview = pd.concat([overview_saved, overview_added], ignore_index=True)
        except UnboundLocalError:
            overview = overview_added
        try:
            activities = pd.concat([activities_saved, activities_added], ignore_index=True)
        except UnboundLocalError:
            activities = activities_added
        overview.to_csv(os.path.join(__backup_path, 'rescuetime_overview.csv'))
        activities.to_csv(os.path.join(__backup_path, 'rescuetime_activities.csv'))

        summary_dict = {
            'date': [],
            'productivity_pulse': [],
            'very_productive_percentage': [],
            'productive_percentage': [],
            'neutral_percentage': [],
            'distracting_percentage': [],
            'very_distracting_percentage': [],
            'all_productive_percentage': [],
            'all_distracting_percentage': [],
            'uncategorized_percentage': [],
            'business_percentage': [],
            'communication_and_scheduling_percentage': [],
            'social_networking_percentage': [],
            'design_and_composition_percentage': [],
            'entertainment_percentage': [],
            'news_percentage': [],
            'software_development_percentage': [],
            'reference_and_learning_percentage': [],
            'shopping_percentage': [],
            'utilities_percentage': [],
            'total_hours': [],
            'very_productive_hours': [],
            'productive_hours': [],
            'neutral_hours': [],
            'distracting_hours': [],
            'very_distracting_hours': [],
            'all_productive_hours': [],
            'all_distracting_hours': [],
            'uncategorized_hours': [],
            'business_hours': [],
            'communication_and_scheduling_hours': [],
            'social_networking_hours': [],
            'design_and_composition_hours': [],
            'entertainment_hours': [],
            'news_hours': [],
            'software_development_hours': [],
            'reference_and_learning_hours': [],
            'shopping_hours': [],
            'utilities_hours': [],
            'total_duration_formatted': [],
            'very_productive_duration_formatted': [],
            'productive_duration_formatted': [],
            'neutral_duration_formatted': [],
            'distracting_duration_formatted': [],
            'very_distracting_duration_formatted': [],
            'all_productive_duration_formatted': [],
            'all_distracting_duration_formatted': [],
            'uncategorized_duration_formatted': [],
            'business_duration_formatted': [],
            'communication_and_scheduling_duration_formatted': [],
            'social_networking_duration_formatted': [],
            'design_and_composition_duration_formatted': [],
            'entertainment_duration_formatted': [],
            'news_duration_formatted': [],
            'software_development_duration_formatted': [],
            'reference_and_learning_duration_formatted': [],
            'shopping_duration_formatted': [],
            'utilities_duration_formatted': []
        }

        daily_summary = f"https://www.rescuetime.com/anapi/daily_summary_feed?key={self.__rescue_key}&restrict_begin={summary_date_save}&restrict_end={today}&format=json"
        summary = requests.get(daily_summary).json() # -> last 14 days
        for day in summary:
            for key in day.keys():
                if key in summary_dict:
                    summary_dict[key].append(day[key])

        summary_added = pd.DataFrame.from_dict(summary_dict)
        summary_added = summary_added.reindex(index=summary_added.index[::-1]).reset_index()
        summary_added.drop(columns = ['index'], inplace=True)
        summary_saved_copy = summary_saved.copy()
        try:
            for i, row in summary_added.iterrows():
                # len_summary = len(summary_saved)
                summary_saved_copy.drop(summary_saved[summary_saved['date'] == row['date']].index, inplace=True)
                # assert len_summary-len(summary_saved)==1
            summary = pd.concat([summary_saved_copy, summary_added], ignore_index=True)
        except UnboundLocalError:
            summary = summary_added
        summary.to_csv(os.path.join(__backup_path, 'rescuetime_summary.csv'))

        print("oe")
        # summary no need to change

        # # top-level categories:
        # # top_cat = {
        # #     'Software Development': ['Visual Studio Code', 'python', 'Github'],
        # #     'Entertainment': ['twitch.tv', 'VLC Media Player', 'tv.twitch.android.app'],
        # #     'Communication & Scheduling': ['Gmail', 'WhatsApp Messenger Android', 'web.whatsapp.com'],
        # #     'Reference & Learning': ['google.com', 'Fitbit for Android', 'dev.fitbit.com'],
        # #     'Business': ['wakatime.com', 'rescuetime.com', 'RescueTime for Android'],
        # #     'Utilities': ['Google Chrome for Android', 'Windows Explorer', 'c:'],
        # #     'Social Networking': ['Instagram for Android', 'linkedin.com'],
        # #     'Shopping': ['galaxus.ch', 'anibis.ch', 'fr.bikester.ch'],
        # #     'Design & Composition': ['OneNote', 'Google Documents'],
        # #     'News & Opinion': ['medium.com', 'ch.admin.meteoswiss'],
        # #     'Uncategorized': []
        # # }

        # # WAKATIME
        # # Warning: 'Coding activity older than 2 weeks is not available on the free plan.'
        # get the last save from the last csv file
        try:
            durations_saved = pd.read_csv(os.path.join(__backup_path, 'wakatime_durations.csv'))
            durations_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            durations_last_save = durations_saved['time'].iloc[-1]
            durations_first_save = False
            heartbeats_saved = pd.read_csv(os.path.join(__backup_path, 'wakatime_heartbeats.csv'))
            heartbeats_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            heartbeats_last_save = heartbeats_saved['time'].iloc[-1]
            heartbeats_first_save = False
        except FileNotFoundError:
            durations_last_save = '2023-10-20 06:00:00'
            heartbeats_last_save = '2023-10-20 06:00:00'
            durations_first_save = True
            heartbeats_first_save = True

        # extra_params = {'start': '2023-10-19', 'end': '2023-10-24'}
        heartbeat_call = f"https://wakatime.com/api/v1/users/current/heartbeats?api_key={self.__waka_key}"
        duration_call = f"https://wakatime.com/api/v1/users/current/durations?api_key={self.__waka_key}"
        # summary_call = f"https://wakatime.com/api/v1/users/current/summaries?api_key={self.__waka_key}" #&start={start}&end={end}"
        # summaries = requests.get(summary_call, params=extra_params).json() # headers = header
        # Setup Iteration - by Day
        durations_date_save = datetime.datetime.strptime(durations_last_save.split(" ")[0], '%Y-%m-%d').date().strftime('%Y-%m-%d')
        heartbeats_date_save = datetime.datetime.strptime(heartbeats_last_save.split(" ")[0], '%Y-%m-%d').date().strftime('%Y-%m-%d')

        heartbeats_dict = {
            'entity': [],
            'type': [],
            'time': [], #-> convert: datetime.datetime.fromtimestamp(heartbeats['data'][0]['time'])
            'project': [],
            'language': [],
            'dependencies': [],
            'is_write': [],
            'category': [],
            'created_at': [],
            'machine_name_id': []
        }
        durations_dict = {
            'time': [],
            'project': [],
            'duration': []
        }

        d1 = datetime.datetime.strptime(heartbeats_date_save,"%Y-%m-%d").date()
        d2 = datetime.date.today()
        delta = d2 - d1
        if delta.days>14:
            d1 = d2 - td(days=14)
            delta = d2 - d1
        # Iterate through the days, making a request per day
        for i in range(delta.days + 1):
            # Find iter date and set begin and end values to this to extract at once.
            d3 = d1 + td(days=i) # Add a day
            if d3.day == 1: print('Pulling Monthly Data for ', d3)

            extra_params = {'date': d3}

            # Request
            try:
                heartbeats = requests.get(heartbeat_call, params=extra_params).json() # Make Request
                # print("Collecting Activities for " + str(d3))
            except Exception as e:
                print(e)
                print("Error collecting data for " + str(d3))

            if len(heartbeats) != 0:
                for i in heartbeats['data']:
                    # entity, type, time -> convert: datetime.datetime.fromtimestamp(heartbeats['data'][0]['time'])
                    # project, language, dependencies, is_write, category, created_at, machine_name_id
                    heartbeats_dict['entity'].append(i['entity'])
                    heartbeats_dict['type'].append(i['type'])
                    heartbeats_dict['time'].append(datetime.datetime.fromtimestamp(i['time']))
                    heartbeats_dict['project'].append(i['project'])
                    heartbeats_dict['language'].append(i['language'])
                    heartbeats_dict['dependencies'].append(i['dependencies'])
                    heartbeats_dict['is_write'].append(i['is_write'])
                    heartbeats_dict['category'].append(i['category'])
                    heartbeats_dict['created_at'].append(i['created_at'])
                    heartbeats_dict['machine_name_id'].append(i['machine_name_id'])
            else:
                print("Appears there is no WakaTime heartbeats data for " + str(d3))


        d1 = datetime.datetime.strptime(durations_date_save,"%Y-%m-%d").date()
        d2 = datetime.date.today()
        delta = d2 - d1
        if delta.days>14:
            d1 = d2 - td(days=14)
            delta = d2 - d1
        # Iterate through the days, making a request per day
        for i in range(delta.days + 1):
            # Find iter date and set begin and end values to this to extract at once.
            d3 = d1 + td(days=i) # Add a day
            if d3.day == 1: print('Pulling Monthly Data for ', d3)

            extra_params = {'date': d3}
            # Request
            try:
                durations = requests.get(duration_call, params=extra_params).json() # Make Request
                # print("Collecting Activities for " + str(d3))
            except Exception as e:
                print(e)
                print("Error collecting data for " + str(d3))
            if len(durations) != 0:
                for i in durations['data']:
                    durations_dict['time'].append(datetime.datetime.fromtimestamp(i['time']))
                    durations_dict['project'].append(i['project'])
                    durations_dict['duration'].append(i['duration'])
            else:
                print("Appears there is no WakaTime durations data for " + str(d3))

        durations_added = pd.DataFrame.from_dict(durations_dict)
        heartbeats_added = pd.DataFrame.from_dict(heartbeats_dict)
        durations_added_copy = durations_added.copy()
        if not durations_first_save:
            for i, row in durations_added.iterrows():
                # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
                # otherwise not
                # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                if row['time']<datetime.datetime.strptime(durations_last_save, "%Y-%m-%d %H:%M:%S.%f"):
                    # remove the row
                    durations_added_copy.drop(i, inplace=True)
                # elif datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")==datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                elif row['time']==datetime.datetime.strptime(durations_last_save, "%Y-%m-%d %H:%M:%S.%f"):
                    len_overview = len(durations_saved)
                    durations_saved.drop(durations_saved[
                        (durations_saved['time'] == durations_last_save) &
                        (durations_saved['project'] == row['project'])].index, inplace=True)
                    assert len_overview-len(durations_saved) == 1
                durations = pd.concat([durations_saved, durations_added], ignore_index=True)
        else:
            durations = durations_added
        durations_added = durations_added_copy
        heartbeats_added_copy = heartbeats_added.copy()
        if not heartbeats_first_save:
            for i, row in heartbeats_added.iterrows():
                # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
                # otherwise not
                # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                if row['time']<datetime.datetime.strptime(heartbeats_last_save, "%Y-%m-%d %H:%M:%S.%f"):
                    # remove the row
                    heartbeats_added_copy.drop(i, inplace=True)
                # elif datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")==datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                elif row['time']==datetime.datetime.strptime(heartbeats_last_save, "%Y-%m-%d %H:%M:%S.%f"):
                    len_heartbeats = len(heartbeats_saved)
                    heartbeats_saved.drop(heartbeats_saved[
                        (heartbeats_saved['time'] == heartbeats_last_save) &
                        (heartbeats_saved['entity'] == row['entity']) &
                        (heartbeats_saved['type'] == row['type']) &
                        (heartbeats_saved['project'] == row['project'])].index, inplace=True)
                    assert len_heartbeats-len(heartbeats_saved) == 1
                heartbeats = pd.concat([heartbeats_saved, heartbeats_added], ignore_index=True)
        else:
            heartbeats = heartbeats_added
        heartbeats_added = heartbeats_added_copy
        durations.to_csv(os.path.join(__backup_path, 'wakatime_durations.csv'))
        heartbeats.to_csv(os.path.join(__backup_path, 'wakatime_heartbeats.csv'))

def get_labels(keys, n):
    labels = []
    for key in keys:
        len_ = len(key)
        if len_>n:
            ind = key.find(' ', len_ // 2 - 1)
            ind = ind if ind > 0 else key.rfind(' ')

            str1 = key[:ind]
            str2 = key[ind+1:]
            labels.append(str1 + '\n' + str2)
        else:
            labels.append(key)
    return labels

