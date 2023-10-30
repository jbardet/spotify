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
from colour import Color
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import requests
import matplotlib.pyplot as plt
from rauth import OAuth2Service
from urllib.parse import parse_qsl
from datetime import timedelta as td

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

    def save_data(self):
        """
        Save the weekly data from the API in a json file
        """
        # get the last save from the last csv file
        try:
            activities_saved = pd.read_csv('data/rescuetime_activities.csv')
            activities_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            # activities_saved.sort_values(by='date', inplace=True)
            # activities_saved.to_csv('data/rescuetime_activities.csv')
            activities_last_save = activities_saved['date'].iloc[-1]
            summary_saved = pd.read_csv('data/rescuetime_summary.csv')
            summary_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            # summary_saved.sort_values(by='date', inplace=True)
            # summary_saved.to_csv('data/rescuetime_summary.csv')
            summary_last_save = activities_saved['date'].iloc[-1]
            overview_saved = pd.read_csv('data/rescuetime_overview.csv')
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
        # last_save = '2023-10-10'
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
                except:
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
                except:
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
        for i, row in overview_added.iterrows():
            # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
            # otherwise not
            # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
            if row['date']<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                # remove the row
                overview_added.drop(i, inplace=True)
            # elif datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")==datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
            elif row['date']==datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                len_overview = len(overview_saved)
                overview_saved.drop(overview_saved[
                    (overview_saved['date'] == overview_last_save) &
                    (overview_saved['category'] == row['category']) &
                    (overview_saved['device'] == row['device'])].index, inplace=True)
                # assert len_overview-len(overview_saved) == 1
        for i, row in activities_added.iterrows():
            # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
            # otherwise not
            # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S") < datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
            if row['date'] < datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
                # remove the row
                activities_added.drop(i, inplace=True)
            # elif datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")==datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
            elif row['date']==datetime.datetime.strptime(activities_last_save, "%Y-%m-%d %H:%M:%S"):
                len_activities = len(activities_saved)
                activities_saved.drop(activities_saved[
                    (activities_saved['date'] == activities_last_save) &
                    (activities_saved['activity'] == row['activity']) &
                    (activities_saved['category'] == row['category']) &
                    (activities_saved['document'] == row['document']) &
                    (activities_saved['productivity'] == row['productivity']) &
                    (activities_saved['device'] == row['device'])].index, inplace=True)
                assert len_activities-len(activities_saved) == 1
        try:
            overview = pd.concat([overview_saved, overview_added], ignore_index=True)
        except UnboundLocalError:
            overview = overview_added
        try:
            activities = pd.concat([activities_saved, activities_added], ignore_index=True)
        except UnboundLocalError:
            activities = activities_added
        overview.to_csv('data/rescuetime_overview.csv')
        activities.to_csv('data/rescuetime_activities.csv')

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
        try:
            for i, row in summary_added.iterrows():
                len_summary = len(summary_saved)
                summary_saved.drop(summary_saved[summary_saved['date'] == row['date']].index, inplace=True)
                assert len_summary-len(summary_saved)==1
            summary = pd.concat([summary_saved, summary_added], ignore_index=True)
        except UnboundLocalError:
            summary = summary_added
        summary.to_csv('data/rescuetime_summary.csv')

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
            durations_saved = pd.read_csv('data/wakatime_durations.csv')
            durations_saved.drop(['Unnamed: 0'], axis=1, inplace=True)
            durations_last_save = durations_saved['time'].iloc[-1]
            durations_first_save = False
            heartbeats_saved = pd.read_csv('data/wakatime_heartbeats.csv')
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
            except:
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
            except:
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
        if not durations_first_save:
            for i, row in durations_added.iterrows():
                # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
                # otherwise not
                # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                if row['time']<datetime.datetime.strptime(durations_last_save, "%Y-%m-%d %H:%M:%S.%f"):
                    # remove the row
                    durations_added.drop(i, inplace=True)
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
        if not heartbeats_first_save:
            for i, row in heartbeats_added.iterrows():
                # when load dtaaframe from csv need to put: datetime.datetime.strptime(exact_last_save, "%Y-%m-%d %H:%M:%S")
                # otherwise not
                # if datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(overview_last_save, "%Y-%m-%d %H:%M:%S"):
                if row['time']<datetime.datetime.strptime(heartbeats_last_save, "%Y-%m-%d %H:%M:%S.%f"):
                    # remove the row
                    heartbeats_added.drop(i, inplace=True)
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
        durations.to_csv('data/wakatime_durations.csv')
        heartbeats.to_csv('data/wakatime_heartbeats.csv')
        print("oe")

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
