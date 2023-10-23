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
from urllib.parse import parse_qsl

from helpers import add_website_link

# TODO: change date in the API calls to today's date from last week? or only today?
# TODO: add a connection to a database to save results (or on disk might be easier)

class RescueWakaTime():
    """
    Integrate a Rescue time window to see your daily activity
    """
    def __init__(self, rescue_key: str, waka_key: str, window: tk.Frame) -> None:
        """
        Initialize the RescueTime class from the API key and the GUI window
        where to place it

        :param key: the user key to access the API
        :type key: str
        :param window: the window where to place the RescueTime widget
        :type window: tk.Frame
        """
        self.__rescue_key = rescue_key
        self.__waka_key = waka_key['key']
        self.window = window
        today = datetime.date.today()
        self.today = f"{today.year}-{today.month}-{today.day}"

        self.start_call = f"https://www.rescuetime.com/anapi/start_focustime?key={self.__rescue_key}&duration=-1"
        self.end_call = f"https://www.rescuetime.com/anapi/end_focustime?key={self.__rescue_key}"
        self.rescue_time_is_on = False # self.is_rescue_time_on()

        self.rank_call = f"https://www.rescuetime.com/anapi/data?key={self.__rescue_key}&perspective=rank&restrict_kind=productivity&interval=hour&restrict_begin={self.today}&restrict_end={self.today}&format=json"
        self.category_call = f"https://www.rescuetime.com/anapi/data?key={self.__rescue_key}&perspective=rank&restrict_kind=document&interval=hour&restrict_begin={self.today}&restrict_end={self.today}&format=json"
        self.activity_call = f"https://www.rescuetime.com/anapi/data?key={self.__rescue_key}&perspective=rank&restrict_kind=activity&interval=hour&restrict_begin={self.today}&restrict_end={self.today}&format=json"

        self.color_palette = self.create_color_palette()

        # self.test_wakatime()
        # self.weekly_save()

    def test_wakatime(self):

        # # OAuth 2.0 authentication needs to visit a page to get a link -> not automatic
        # # So I will use an API key for now
        # if sys.version_info[0] == 3:
        #     raw_input = input

        # client_id = ""
        # client_secret = ""

        # self.wakatime_service = OAuth2Service(
        #     client_id=client_id,  # your App ID from https://wakatime.com/apps
        #     client_secret=client_secret,  # your App Secret from https://wakatime.com/apps
        #     name='wakatime',
        #     authorize_url='https://wakatime.com/oauth/authorize',
        #     access_token_url='https://wakatime.com/oauth/token',
        #     base_url='https://wakatime.com/api/v1/')
        # redirect_uri = 'https://wakatime.com/oauth/test'
        # state = hashlib.sha1(os.urandom(40)).hexdigest()
        # params = {'scope': 'email,read_stats,read_logged_time,read_private_leaderboards',
        #         'response_type': 'code',
        #         'state': state,
        #         'redirect_uri': redirect_uri}

        # url = self.wakatime_service.get_authorize_url(**params)
        # print(url)
        # headers = {'Accept': 'application/x-www-form-urlencoded'}
        # code = raw_input('Enter code from url: ')
        # session = self.wakatime_service.get_auth_session(headers=headers,
        #                                                  data={'code': code,
        #                                                        'grant_type': 'authorization_code',
        #                                                        'redirect_uri': redirect_uri})
        # user = session.get('users/current').json()
        # stats = session.get('users/current/stats')

        # # refresh token
        # refresh_token = dict(parse_qsl(session.access_token_response.text))['refresh_token']
        # data = {
        #     'grant_type': 'refresh_token',
        #     'client_id': client_id,
        #     'client_secret': client_secret,
        #     'refresh_token': refresh_token,
        # }
        # resp = requests.post('https://wakatime.com/oauth/token', data=data)

        # print(user)
        # print(stats.text)
        # extra_params = {'start': '2023-10-20', 'end': '2023-10-23'}
        # summaries = session.get('users/current/summaries', params=extra_params).json()
        # print("oe")

        # header = {
        #     'Authorization': f'Basic ' + api_key,
        #     'scope': 'email,read_stats,read_logged_time,read_private_leaderboards'
        # }
        extra_params = {'start': '2023-10-20', 'end': '2023-10-23'}
        summary_call = "https://wakatime.com/api/v1/users/current/summaries?api_key="+self.__waka_key
        # response = requests.get(summary_call, params=extra_params).json() # headers = header

    def weekly_save(self):
        """
        Save the weekly data from the API in a json file
        """
        # RescueTime
        baseurl = 'https://www.rescuetime.com/anapi/data?key='
        url = baseurl+self.__rescue_key
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

        # self.add_wakatime_plot()

    # def add_wakatime_plot(self):
    #     self.test_wakatime()

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
        response = requests.get(self.activity_call)
        data_activity = response.json()
        with open("data_activity.pickle", "wb") as file:
            pickle.dump(data_activity, file)
        with open('data_activity.pickle', 'rb') as handle:
            data_activity = pickle.load(handle)

        df = pd.DataFrame(data_activity['rows'],
                          columns = ['rank', 'time', 'people', 'activity',
                                     'category', 'productivity'])
        self.add_ranked_plot(df.groupby("productivity").sum()['time'])
        self.add_categorical_plot(df)
        # self.add_activity_plot(df)
        self.add_wakatime_plot(df)

    def add_wakatime_plot(self, df: pd.DataFrame) -> None:
        status_call = "https://wakatime.com/api/v1/users/current/status_bar/today?api_key="+self.__waka_key
        status_bar = requests.get(status_call).json()
        with open("status_bar.pickle", "wb") as file:
            pickle.dump(status_bar, file)
        with open('status_bar.pickle', 'rb') as handle:
            status_bar = pickle.load(handle)
        # status bar: ['grand_total', 'range', 'projects', 'languages', 'dependencies', 'machines', 'editors', 'operating_systems', 'categories']
        rt_tot_time = df['time'].sum()/3600
        rt_prod_time = df.groupby('productivity').sum()['time'][2]/3600
        rt_vs_time = df.groupby('activity').sum()['time']['Visual Studio Code']/3600
        total_today = status_bar['data']['grand_total']['decimal']
        categories = status_bar['data']['categories']
        # Make the plot and add it to the GUI window
        fig, (self.ax) = plt.subplots(1, 1, figsize=(5,4))
        plt.title("Time analysis")
        plt.ylabel("Time (hours)")
        labels = ["RT_tot", "RT_prod", "RT_VS", "WT_tot"] + [cat['name'] for cat in categories]
        values = [rt_tot_time, rt_prod_time, rt_vs_time, float(total_today)] + [float(cat['decimal']) for cat in categories]
        plt.bar(labels, values, color='blue')
        # Add angle to the labels to see all labels entirely
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side = tk.TOP)


    def add_activity_plot(self, df: pd.DataFrame) -> None:
        # response = requests.get(self.activity_call)
        # data_activity = response.json()
        # with open("data_activity.pickle", "wb") as file:
        #     pickle.dump(data_activity, file)
        with open('data_activity.pickle', 'rb') as handle:
            data_activity = pickle.load(handle)

        # print(data_activity)
        # # Make a vertical bar chart with the category and productivity score
        # # Sort the Serie by value and only show the 10 biggest categories on the plot
        top_ten = df.groupby("activity").sum()['time'].sort_values(ascending=False)[:10]
        plot_colors = [self.color_palette[2-df[df['activity'] ==cat]['productivity'].iloc[0]]
                       for cat in top_ten.keys()]

        # Make the plot and add it to the GUI window
        fig, (self.ax) = plt.subplots(1, 1, figsize=(5,4))
        plt.title("Activities")
        plt.ylabel("Time (hours)")
        plt.bar(top_ten.keys(), top_ten.values/3600, color=plot_colors)
        # Add angle to the labels to see all labels entirely
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side = tk.TOP)

    def add_ranked_plot(self, rank: pd.Series) -> None:
        """
        Make the ranked plot and add to the GUI
        """
        # # Get the ranked data from the API
        # response = requests.get(self.rank_call)
        # data_rank = response.json()
        # with open("data_prod_rank.pickle", "wb") as file:
        #     pickle.dump(data_rank, file)
        # with open('data_prod_rank.pickle', 'rb') as handle:
        #     data_rank = pickle.load(handle)

        # Make a horizontal bar chart with the productivity score [-2,2] and
        # the time spent in hours
        data_to_plot = [[] for _ in range(len(rank))]
        for key, value in rank.items():
            data_to_plot[2-key] = [key, value]

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

    def add_categorical_plot(self, df: pd.DataFrame) -> None:
        """
        Make the categorical plot and add to the GUI
        """
        # # # Get the categorical data from the API
        # # response = requests.get(self.category_call)
        # # data_cat = response.json()
        # # with open("data6.pickle", "wb") as file:
        # #     pickle.dump(data_cat, file)
        # with open('data6.pickle', 'rb') as handle:
        #     data_cat = pickle.load(handle)

        # # Make a vertical bar chart with the category and productivity score
        # # Sort the Serie by value and only show the 10 biggest categories on the plot
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

# WAKATIME

# ['data'], ['is_up_to_date', 'range', 'timeout', 'percent_calculated', 'total_seconds', 'text', 'decimal', 'digital']
# all_time_since_today = session.get('users/current/all_time_since_today').json()
# # need date, ['data'], list of {'time': 1697948285.120785, 'project': 'spotify', 'duration': 3081.478932, 'color': None}
# extra_params = {'date': '2023-10-22'}
# durations = session.get('users/current/durations', params=extra_params).json()
# # need date, ['data'], gives nothing?
# external_durations = session.get('users/current/external_durations', params=extra_params).json()
# # goal = session.get('users/current/goals/:goal').text
# # empty for now
# goals = session.get('users/current/goals').json()
# # need date, ['data'], list of dict_keys(['id', 'entity', 'type', 'time', 'project', 'project_root_count', 'branch', 'language', 'dependencies', 'lines', 'lineno', 'cursorpos', 'is_write', 'category', 'created_at', 'user_id', 'user_agent_id', 'machine_name_id'])
# heartbeats = session.get('users/current/heartbeats', params=extra_params).json()
# # replace:
# # insight_type = days, best_day, daily_average, projects, languages, editors, categories, machines, or operating_systems
# # range = YYYY, YYYY-MM, last_7_days, last_30_days, last_6_months, last_year, or all_time
# # for accounts subscribed to the free plan, time ranges >= one year are updated on the first request.
# # e.g. daily_average last_7_days -> premium only -> only works with last_year: 'current_user': {'total': {'seconds': 25430.510746, 'text': '7 hrs 3 mins'}, 'daily_average': {'seconds': 69, 'text': '1 min'}}
# # days -> last_year only -> list of 365 days with 'date0, 'total' 'categories' [{'name': 'Debugging', 'total': 2273.59264}, {'name': 'Coding', 'total': 415.909864}]
# # projects -> last_year only -> [{'total_seconds': 21621.457172, 'name': 'spotify'}, {'total_seconds': 1435.964871, 'name': 'personal-influxdb'}]
# # languages -> last_year only ->  [{'name': 'Python', 'total_seconds': 23041.451302}, {'name': 'Other', 'total_seconds': 15.970741}
# # editors -> last_year only -> [{'total_seconds': 23057.422043, 'name': 'VS Code'}]
# # categories -> last_year only -> [{'name': 'Coding', 'total_seconds': 11818.206905}, {'name': 'Debugging', 'total_seconds': 11239.215138}]
# # machines -> last_year only -> [{'total_seconds': 23057.422043, 'name': 'DESKTOP-L58EQH4', 'machine_name_id': '018b4c4e-87d3-487a-b...e649819022'}]
# # operating_systems -> last_year only -> [{'total_seconds': 23057.422043, 'name': 'Windows'}]
# # insights = session.get('users/current/insights/:insight_type/:range').json()

# # not very useful
# leaders = session.get('/api/v1/leaders').json()
# # list ['id', 'value', 'ip', 'timezone', 'last_seen_at', 'created_at', 'name']
# machine_names = session.get('users/current/machine_names').json()
# # empty
# leaderboards = session.get('users/current/leaderboards').json()
# # useless
# languages = session.get('/api/v1/program_languages').json()
# # list of ['id', 'name', 'color', 'last_heartbeat_at', 'created_at', 'badge', 'clients', 'repository', 'human_readable_last_heartbeat_at', 'url', 'urlencoded_name', 'has_public_url']
# projects = session.get('users/current/projects').json()
# # ? ['status', 'is_up_to_date', 'is_up_to_date_pending_future', 'is_stuck', 'is_already_updating', 'range', 'percent_calculated', 'timeout', 'writes_only', 'username', 'is_including_today', 'human_readable_range', 'is_coding_activity_visible', 'is_other_usage_visible']
# stats = session.get('users/current/stats').json()
# # rabge can be YYYY-MM, last_7_days, last_30_days, last_6_months, last_year, or all_time
# # stats_range = session.get('users/current/stats/:range').text
# # ['grand_total', 'range', 'projects', 'languages', 'dependencies', 'machines', 'editors', 'operating_systems', 'categories']
# status_bar = session.get('users/current/status_bar/today').json()
# # need start and end date
# # 'data' -> ['languages', 'grand_total', 'editors', 'operating_systems', 'categories', 'dependencies', 'machines', 'projects', 'range'])
# # 'cumulative_total': {'seconds': 26447.587896, 'text': '7 hrs 20 mins', 'digital': '7:20', 'decimal': '7.33'}
# # ['daily_average']: ['holidays', 'days_minus_holidays', 'days_including_holidays', 'seconds', 'seconds_including_other_language', 'text', 'text_including_other_language'])
# extra_params = {'start': '2023-10-20', 'end': '2023-10-23'}
# summaries = session.get('users/current/summaries', params=extra_params).json()
# # list of ['id', 'value', 'created_at', 'os', 'version', 'go_version', 'last_seen_at', 'editor', 'cli_version']
# user_agents = session.get('users/current/user_agents').json()
# # information on user
# _user = session.get('users/current').json()
# dict = {"all_time_since_today": all_time_since_today,
#         "durations": durations,
#         "external_durations": external_durations,
#         "goals": goals,
#         "heartbeats": heartbeats,
#         "leaders": leaders,
#         "machine_names": machine_names,
#         "leaderboards": leaderboards,
#         "languages": languages,
#         "projects": projects,
#         "stats": stats,
#         "status_bar": status_bar,
#         "summaries": summaries,
#         "user_agents": user_agents,
#         "_user": _user}
# import pickle
# import ast
# with open('./Wakatime/wakatime.pickle', 'wb') as file:
#     pickle.dump(dict, file)
