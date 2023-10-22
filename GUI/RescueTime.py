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
from colour import Color
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import requests
import matplotlib.pyplot as plt
from rauth import OAuth2Service

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
        # self.__key = key
        # self.window = window

        # self.start_call = f"https://www.rescuetime.com/anapi/start_focustime?key={self.__key}&duration=-1"
        # self.end_call = f"https://www.rescuetime.com/anapi/end_focustime?key={self.__key}"
        # self.rescue_time_is_on = False # self.is_rescue_time_on()

        # self.rank_call = f"https://www.rescuetime.com/anapi/data?key={self.__key}&perspective=rank&restrict_kind=productivity&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"
        # self.category_call = f"https://www.rescuetime.com/anapi/data?key={self.__key}&perspective=rank&restrict_kind=document&interval=hour&restrict_begin=2023-10-10&restrict_end=2023-10-17&format=json"

        # self.color_palette = self.create_color_palette()
        self.test_wakatime()

        self.weekly_save()

    def test_wakatime(self):
        if sys.version_info[0] == 3:
            raw_input = input
        self.wakatime_service = OAuth2Service(
            client_id="",  # your App ID from https://wakatime.com/apps
            client_secret="",  # your App Secret from https://wakatime.com/apps
            name='wakatime',
            authorize_url='https://wakatime.com/oauth/authorize',
            access_token_url='https://wakatime.com/oauth/token',
            base_url='https://wakatime.com/api/v1/')
        redirect_uri = 'https://wakatime.com/oauth/test'
        state = hashlib.sha1(os.urandom(40)).hexdigest()
        params = {'scope': 'email,read_stats,read_logged_time,read_private_leaderboards',
                'response_type': 'code',
                'state': state,
                'redirect_uri': redirect_uri}

        url = self.wakatime_service.get_authorize_url(**params)
        print(url)
        headers = {'Accept': 'application/x-www-form-urlencoded'}
        code = raw_input('Enter code from url: ')
        session = self.wakatime_service.get_auth_session(headers=headers,
                                                         data={'code': code,
                                                               'grant_type': 'authorization_code',
                                                               'redirect_uri': redirect_uri})
        user = session.get('users/current').json()
        stats = session.get('users/current/stats')
        print(user)
        print(stats.text)
        # ['data'], ['is_up_to_date', 'range', 'timeout', 'percent_calculated', 'total_seconds', 'text', 'decimal', 'digital']
        all_time_since_today = session.get('users/current/all_time_since_today').json()
        # need date, 
        durations = session.get('users/current/durations/2023-10-20').json()
        # need date, 
        external_durations = session.get('users/current/external_durations').json()
        # goal = session.get('users/current/goals/:goal').text
        # empty for now
        goals = session.get('users/current/goals').json()
        # need date
        heartbeats = session.get('users/current/heartbeats').json()
        # replace:
        # insight_type = weekday, days, best_day, daily_average, projects, languages, editors, categories, machines, or operating_systems
        # range = YYYY, YYYY-MM, last_7_days, last_30_days, last_6_months, last_year, or all_time
        # for accounts subscribed to the free plan, time ranges >= one year are updated on the first request.
        # insights = session.get('users/current/insights/:insight_type/:range').text

        # not very useful
        leaders = session.get('/api/v1/leaders').json()
        # list ['id', 'value', 'ip', 'timezone', 'last_seen_at', 'created_at', 'name']
        machine_names = session.get('users/current/machine_names').json()
        # 
        leaderboards = session.get('users/current/leaderboards').json()
        # useless
        languages = session.get('/api/v1/program_languages').json()
        # list of ['id', 'name', 'color', 'last_heartbeat_at', 'created_at', 'badge', 'clients', 'repository', 'human_readable_last_heartbeat_at', 'url', 'urlencoded_name', 'has_public_url']
        projects = session.get('users/current/projects').json()
        # ? ['status', 'is_up_to_date', 'is_up_to_date_pending_future', 'is_stuck', 'is_already_updating', 'range', 'percent_calculated', 'timeout', 'writes_only', 'username', 'is_including_today', 'human_readable_range', 'is_coding_activity_visible', 'is_other_usage_visible']
        stats = session.get('users/current/stats').json()
        # rabge can be YYYY-MM, last_7_days, last_30_days, last_6_months, last_year, or all_time
        # stats_range = session.get('users/current/stats/:range').text
        # ['grand_total', 'range', 'projects', 'languages', 'dependencies', 'machines', 'editors', 'operating_systems', 'categories']
        status_bar = session.get('users/current/status_bar/today').json()
        # need date
        summaries = session.get('users/current/summaries').json()
        # list of ['id', 'value', 'created_at', 'os', 'version', 'go_version', 'last_seen_at', 'editor', 'cli_version']
        user_agents = session.get('users/current/user_agents').json()
        # information on user
        _user = session.get('users/current').json()
        dict = {"all_time_since_today": all_time_since_today,
                "durations": durations,
                "external_durations": external_durations,
                "goals": goals,
                "heartbeats": heartbeats,
                "leaders": leaders,
                "machine_names": machine_names,
                "leaderboards": leaderboards,
                "languages": languages,
                "projects": projects,
                "stats": stats,
                "status_bar": status_bar,
                "summaries": summaries,
                "user_agents": user_agents,
                "_user": _user}
        import pickle
        import ast
        with open('./Wakatime/wakatime.pickle', 'wb') as file:
            pickle.dump(dict, file)
        print("oe")

    def weekly_save(self):
        """
        Save the weekly data from the API in a json file
        """
        # RescueTime
        baseurl = 'https://www.rescuetime.com/anapi/data?key='
        url = baseurl+self.__key
        today = datetime.date.today()
        last_save = "2023-10-10"
        activities_list = rescuetime_get_activities(url, today, last_save)

        # Get the data by day
        # activities_day_log = rescuetime_get_activities(start_date, end_date, 'day')
        # activities_daily = pd.DataFrame.from_dict(activities_day_log)
        # activities_daily.info()
        # activities_daily.describe()
        # activities_daily.tail()

        # Get the data by hour
        # activities_hour_log = rescuetime_get_activities(start_date, end_date, 'hour')
        # activities_hourly = pd.DataFrame.from_dict(activities_hour_log)
        # activities_hourly.columns = ['Date', 'Seconds', 'NumberPeople', 'Actitivity', 'Document', 'Category', 'Productivity']
        # activities_hourly.info()
        # activities_hourly.describe()
        # activities_hourly.tail()
        # activities_hourly.to_csv('data/rescuetime-hourly-' + start_date + '-to-' + end_date + '.csv')

        # Get the data by minute
        # activities_minute_log = rescuetime_get_activities(start_date, end_date, 'minute')
        # activities_per_minute = pd.DataFrame.from_dict(activities_minute_log)
        # Date', u'Time Spent (seconds)', u'Number of People', u'Activity', u'Document', u'Category', u'Productivity'
        # activities_per_minute.columns = ['Date', 'Seconds', 'NumberPeople', 'Actitivity', 'Document', 'Category', 'Productivity']
        # activities_per_minute.head()
        # activities_per_minute.info()
        # activities_per_minute.describe()
        # activities_per_minute.to_csv('data/rescuetime-by-minute' + start_date + '-to-' + end_date + '.csv')
        print("oe")

        # Wakatime
        

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

        text = "RescueTime"
        url = "https://www.rescuetime.com/rtx/reports/activities"
        self.add_website_link(text, url)

        # TODO: Also add a button either to oy.system to open RescueTime app
        # to add offline work or make a widget to add offline work

        self.add_analytics_plots()
        self.add_start_rescue_time_button()

        text = "Wakatime"
        url = "https://wakatime.com/dashboard"
        self.add_website_link(text, url)

    def add_website_link(self, text: str, url: str) -> None:
        """
        Add a label to access the RescueTime website for analytics

        :param text: the text to display
        :type text: str
        :param url: the link to be clicked
        :type url: str
        """
        font= ('Aerial 12')
        side = "top"
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

# Adjustable by Time Period
def rescuetime_get_activities(url, start_date, end_date, resolution='hour'):
    # Configuration for Query
    # SEE: https://www.rescuetime.com/apidoc
    payload = {
        'perspective':'interval',
        'resolution_time': resolution, #1 of "month", "week", "day", "hour", "minute"
        'restrict_kind':'document',
        'restrict_begin': start_date,
        'restrict_end': end_date,
        'format':'json' #csv
    }

    # Setup Iteration - by Day
    d1 = datetime.strptime(payload['restrict_begin'], "%Y-%m-%d").date()
    d2 = datetime.strptime(payload['restrict_end'], "%Y-%m-%d").date()
    delta = d2 - d1

    activities_list = []

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
        except:
            print("Error collecting data for " + str(d3))

        if len(iter_result) != 0:
            for i in iter_result['rows']:
                activities_list.append(i)
        else:
            print("Appears there is no RescueTime data for " + str(d3))

    return activities_list

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
