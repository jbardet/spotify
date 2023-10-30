import fitbit
import numpy as np
import pandas as pd
import datetime
import dateutil.parser
import seaborn
import time
import json
import requests
import base64
from typing import Dict

class Fitbit:
    def __init__(self, credentials: dict):
        self.__client_secret = credentials['CLIENT_SECRET']
        self.__client_id = credentials['CLIENT_ID']
        self.__user_id = credentials['USER_ID']
        self.__access_token = credentials['ACCESS_TOKEN']
        self.__refresh_token = credentials['REFRESH_TOKEN']
        self.client = fitbit.Fitbit(self.__user_id, self.__client_secret,
                                    oauth2=True, access_token=self.__access_token,
                                    refresh_token=self.__refresh_token)

    def refresh_token(self):
        client_creds = f"{self.__client_id}:{self.__client_secret}"
        base64_creds = client_creds.encode('ascii')
        byte_creds = base64.b64encode(base64_creds)
        message = byte_creds.decode('ascii')
        headers = {
            'Authorization': "Basic "+message,
            'Content-Type': "application/x-www-form-urlencoded"
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.__refresh_token
        }
        r = requests.post("https://api.fitbit.com/oauth2/token", headers=headers, data=data)
        dict = r.json()
        self.__access_token = dict['access_token']
        self.__refresh_token = dict['refresh_token']
        # rewrite to the json file
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
        credentials['fitbit']['ACCESS_TOKEN'] = self.__access_token
        credentials['fitbit']['REFRESH_TOKEN'] = self.__refresh_token
        with open('credentials.json', 'w') as f:
            json.dump(credentials, f)
        self.client = fitbit.Fitbit(self.__user_id, self.__client_secret,
                                    oauth2=True,
                                    access_token=self.__access_token,
                                    refresh_token=self.__refresh_token)

    def save_data(self):

        last_save = "2023-10-22"
        today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        # list of dates to check
        dates_list = []
        start = datetime.datetime.strptime(last_save, '%Y-%m-%d')
        end = datetime.datetime.strptime(today, '%Y-%m-%d')
        step = datetime.timedelta(days=1)
        while start <= end:
            dates_list.append(start.date().strftime("%Y-%m-%d"))
            start += step

        # for time_series you can also specify base_date='today', period=None, end_date=None
        # for intraday time serie - > base_date='today', detail_level='1min', start_time=None, end_time=None
        # and detail_level must be 1sec, 1min or 15min

        # download daily steps data
        # Get Steps Data in JSON from Last Year
        # try:
        #     steps_ts = self.client.time_series('activities/steps', base_date=last_save, end_date=today)
        # except fitbit.exceptions.HTTPUnauthorized:
        #     self.refresh_token()
        #     steps_ts = self.client.time_series('activities/steps', base_date=last_save, end_date=today)
        self.refresh_token()
        headers = {
            'Authorization': 'Bearer ' + self.__access_token
        }

        spacing = 1 # minutes
        t = [str(i*datetime.timedelta(minutes=spacing)) for i in range(24*60//spacing)]
        t = ["0"+m if len(m)<8 else m for m in t]
        # intraday is per day specific fso need to iterate trough the days
        # intraday_dict = {
        #     'date': [],
        #     'time': [],
        #     'steps': [],
        #     'minutesVeryActive': [],
        #     'minutesFairlyActive': [],
        #     'minutesLightlyActive': [],
        #     'minutesSedentary': [],
        #     'elevation': [],
        #     'floors': [],
        #     'distance': [],
        #     'calories': [],
        #     'heart': [],
        # }
        day_dict = {
            'date': [],
            'temp': [],
            'activityCalories': [],
            'br_deepSleepSummary': [],
            'br_remSleepSummary': [],
            'br_fullSleepSummary': [],
            'br_lightSleepSummary': [],
            'activeScore': [],
            'caloriesBMR': [],
            'caloriesOut': [],
            'restingHeartRate': [],
            'marginalCalories': [],
            'out_of_range_calories_out': [],
            'fat_burn_calories_out': [],
            'cardio_calories_out': [],
            'peak_calories_out': [],
            'out_of_range_minutes': [],
            'fat_burn_minutes': [],
            'cardio_minutes': [],
            'peak_minutes': []
        }
        # spo2_dict = {
        #     'date': [],
        #     'value': []
        # }
        # hrv_dict = {
        #     'date': [],
        #     'rmssd': [],
        #     'coverage': [],
        #     'hf': [],
        #     'lf': []
        # }
        # activities_dict = {
        #     'date': [],
        #     'activities': [],
        #     # 'goals': [],
        #     'summary': []
        # }
        # sleep_daily_dict = {
        #     'date': [],
        #     'duration': [],
        #     'efficiency': [],
        #     'endTime': [],
        #     'infoCode': [],
        #     'isMainSleep': [],
        #     'minutesAfterWakeup': [],
        #     'minutesAsleep': [],
        #     'minutesAwake': [],
        #     'minutesToFallAsleep': [],
        #     'startTime': [],
        #     'timeInBed': [],
        #     'type': [],
        #     'logType': [],
        #     'deep_count': [],
        #     'deep_minutes': [],
        #     'deep_thirtyDayAvgMinutes': [],
        #     'light_count': [],
        #     'light_minutes': [],
        #     'light_thirtyDayAvgMinutes': [],
        #     'rem_count': [],
        #     'rem_minutes': [],
        #     'rem_thirtyDayAvgMinutes': [],
        #     'wake_count': [],
        #     'wake_minutes': [],
        #     'wake_thirtyDayAvgMinutes': [],
        #     'asleep_count': [],
        #     'asleep_minutes': [],
        #     'awake_count': [],
        #     'awake_minutes': [],
        #     'restless_count': [],
        #     'restless_minutes': []
        # }
        # sleep_intrad_dict = {
        #     'time': [],
        #     'level': [],
        #     'seconds': []
        # }
        # # Warning: 150 requests per hour
        # for i, date in enumerate(dates_list):
        #     steps_intrad = self.client.intraday_time_series('activities/steps', base_date=date)
        #     minutesVeryActive_intrad = self.client.intraday_time_series('activities/minutesVeryActive', base_date=date)
        #     minutesFairlyActive_intrad = self.client.intraday_time_series('activities/minutesFairlyActive', base_date=date)
        #     minutesLightlyActive_intrad = self.client.intraday_time_series('activities/minutesLightlyActive', base_date=date)
        #     minutesSedentary_intrad = self.client.intraday_time_series('activities/minutesSedentary', base_date=date)
        #     elevation_intrad = self.client.intraday_time_series('activities/elevation', base_date=date)
        #     floors_intrad = self.client.intraday_time_series('activities/floors', base_date=date)
        #     distance_intrad = self.client.intraday_time_series('activities/distance', base_date=date)
        #     calories_intrad = self.client.intraday_time_series('activities/calories', base_date=date)
        #     hr_intrad = self.client.intraday_time_series('activities/heart', base_date=date)
        #     intraday_dict['date'].extend([date for _ in range(len(t))])
        #     intraday_dict['time'].extend(t)
        #     intraday_dict['steps'].extend(fill_dic(steps_intrad['activities-steps-intraday']['dataset'], t))
        #     intraday_dict['minutesVeryActive'].extend(fill_dic(minutesVeryActive_intrad['activities-minutesVeryActive-intraday']['dataset'], t))
        #     intraday_dict['minutesFairlyActive'].extend(fill_dic(minutesFairlyActive_intrad['activities-minutesFairlyActive-intraday']['dataset'], t))
        #     intraday_dict['minutesLightlyActive'].extend(fill_dic(minutesLightlyActive_intrad['activities-minutesLightlyActive-intraday']['dataset'], t))
        #     intraday_dict['minutesSedentary'].extend(fill_dic(minutesSedentary_intrad['activities-minutesSedentary-intraday']['dataset'], t))
        #     intraday_dict['elevation'].extend(fill_dic(elevation_intrad['activities-elevation-intraday']['dataset'], t))
        #     intraday_dict['floors'].extend(fill_dic(floors_intrad['activities-floors-intraday']['dataset'], t))
        #     intraday_dict['calories'].extend(fill_dic(calories_intrad['activities-calories-intraday']['dataset'], t))
        #     intraday_dict['distance'].extend(fill_dic(distance_intrad['activities-distance-intraday']['dataset'], t))
        #     intraday_dict['heart'].extend(fill_dic(hr_intrad['activities-heart-intraday']['dataset'], t))
        #     if not all((i+1)*len(t) == len(d) for d in list(intraday_dict.values())):
        #         print("no")
        #     day_dict['date'].append(date)
        #     temp_ts = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/temp/skin/date/{date}.json", headers = headers).json()
        #     try:
        #         day_dict['temp'].append(temp_ts['tempSkin'][0]['value']['nightlyRelative'])
        #         if len(temp_ts['tempSkin'])>1:
        #             print("oupsi")
        #     except IndexError:
        #         day_dict['temp'].append(np.nan)
            # summary = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/activities/date/{date}.json", headers = headers).json()
            # day_dict['activeScore'].append(summary['activeScore'])
            # day_dict['caloriesBMR'].append(summary['caloriesBMR'])
            # day_dict['caloriesOut'].append(summary['caloriesOut'])
            # day_dict['restingHeartRate'].append(summary['restingHeartRate'])
            # day_dict['marginalCalories'].append(summary['marginalCalories'])
            # # zones are Out of range (30-105bpm), Fat Burn (105-134bpm), Cardio (134-171bpm), Peak (171-220bpm)
            # day_dict['out_of_range_calories_out'].append(summary['heartRateZones'][0]['caloriesOut'])
            # day_dict['fat_burn_calories_out'].append(summary['heartRateZones'][1]['caloriesOut'])
            # day_dict['cardio_calories_out'].append(summary['heartRateZones'][2]['caloriesOut'])
            # day_dict['peak_calories_out'].append(summary['heartRateZones'][3]['caloriesOut'])
            # day_dict['out_of_range_minutes'].append(summary['heartRateZones'][0]['minutes'])
            # day_dict['fat_burn_minutes'].append(summary['heartRateZones'][1]['minutes'])
            # day_dict['cardio_minutes'].append(summary['heartRateZones'][2]['minutes'])
            # day_dict['peak_minutes'].append(summary['heartRateZones'][3]['minutes'])
        #     activityCalories_intrad = self.client.intraday_time_series('activities/activityCalories', base_date=date)
        #     day_dict['activityCalories'].append(int(activityCalories_intrad['activities-activityCalories'][0]['value']))
        #     if len(activityCalories_intrad['activities-activityCalories'])>1:
        #         print("oupsi")
        #     spO2_intrad = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/spo2/date/{date}/all.json", headers = headers).json()
        #     try:
        #         spo2_dict['date'].extend([sp['minute'] for sp in spO2_intrad['minutes']])
        #         spo2_dict['value'].extend([sp['value'] for sp in spO2_intrad['minutes']])
        #     except KeyError:
        #         pass
        #     hrv_intrad = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/hrv/date/{date}/all.json", headers = headers).json()
        #     hrv_dict['date'].extend([hrv['minute'] for hrv in hrv_intrad['hrv'][0]['minutes']])
        #     hrv_dict['rmssd'].extend([hrv['value']['rmssd'] for hrv in hrv_intrad['hrv'][0]['minutes']])
        #     hrv_dict['coverage'].extend([hrv['value']['coverage'] for hrv in hrv_intrad['hrv'][0]['minutes']])
        #     hrv_dict['hf'].extend([hrv['value']['hf'] for hrv in hrv_intrad['hrv'][0]['minutes']])
        #     hrv_dict['lf'].extend([hrv['value']['lf'] for hrv in hrv_intrad['hrv'][0]['minutes']])
        #     if len(hrv_intrad['hrv'])>1:
        #         print("oupsi")
        #     br_date_intrad = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/br/date/{date}/all.json", headers = headers).json()
        #     try:
        #         day_dict['br_deepSleepSummary'].append(br_date_intrad['br'][0]['value']['deepSleepSummary']['breathingRate'])
        #         day_dict['br_remSleepSummary'].append(br_date_intrad['br'][0]['value']['remSleepSummary']['breathingRate'])
        #         day_dict['br_fullSleepSummary'].append(br_date_intrad['br'][0]['value']['fullSleepSummary']['breathingRate'])
        #         day_dict['br_lightSleepSummary'].append(br_date_intrad['br'][0]['value']['lightSleepSummary']['breathingRate'])
        #         if len(br_date_intrad['br'])>1:
        #             print('oupsi')
        #     except IndexError:
        #         day_dict['br_deepSleepSummary'].append(np.nan)
        #         day_dict['br_remSleepSummary'].append(np.nan)
        #         day_dict['br_fullSleepSummary'].append(np.nan)
        #         day_dict['br_lightSleepSummary'].append(np.nan)
        #     activities = self.client.activities(date = date)
        #     activities_dict['date'].append(date)
        #     activities_dict['activities'].append(activities['activities'])
        #     # activities_dict['goals'].append(activities['goals'])
        #     activities_dict['summary'].append(activities['summary'])
        #     sleep = requests.get(f"https://api.fitbit.com/1.2/user/{self.__user_id}/sleep/date/{date}.json", headers = headers).json()
        #     # I don't think I can put sleep into the day dataframe as I might have multiple sleep a day (sieste)
        #     for sleep_session in sleep['sleep']:
        #         sleep_daily_dict['date'].append(sleep_session['dateOfSleep'])
        #         sleep_daily_dict['duration'].append(sleep_session['duration'])
        #         sleep_daily_dict['efficiency'].append(sleep_session['efficiency'])
        #         sleep_daily_dict['endTime'].append(sleep_session['endTime'])
        #         sleep_daily_dict['infoCode'].append(sleep_session['infoCode'])
        #         sleep_daily_dict['isMainSleep'].append(sleep_session['isMainSleep'])
        #         sleep_daily_dict['minutesAfterWakeup'].append(sleep_session['minutesAfterWakeup'])
        #         sleep_daily_dict['minutesAsleep'].append(sleep_session['minutesAsleep'])
        #         sleep_daily_dict['minutesAwake'].append(sleep_session['minutesAwake'])
        #         sleep_daily_dict['minutesToFallAsleep'].append(sleep_session['minutesToFallAsleep'])
        #         sleep_daily_dict['startTime'].append(sleep_session['startTime'])
        #         sleep_daily_dict['timeInBed'].append(sleep_session['timeInBed'])
        #         sleep_daily_dict['type'].append(sleep_session['type'])
        #         sleep_daily_dict['logType'].append(sleep_session['logType'])
        #         sleep_intrad_dict['time'].extend([s['dateTime'] for s in sleep_session['levels']['data']])
        #         sleep_intrad_dict['level'].extend([s['level'] for s in sleep_session['levels']['data']])
        #         sleep_intrad_dict['seconds'].extend([s['seconds'] for s in sleep_session['levels']['data']])
        #         try:
        #             sleep_daily_dict['deep_count'].append(sleep_session['levels']['summary']['deep']['count'])
        #             sleep_daily_dict['deep_minutes'].append(sleep_session['levels']['summary']['deep']['minutes'])
        #             sleep_daily_dict['deep_thirtyDayAvgMinutes'].append(sleep_session['levels']['summary']['deep']['thirtyDayAvgMinutes'])
        #             sleep_daily_dict['light_count'].append(sleep_session['levels']['summary']['light']['count'])
        #             sleep_daily_dict['light_minutes'].append(sleep_session['levels']['summary']['light']['minutes'])
        #             sleep_daily_dict['light_thirtyDayAvgMinutes'].append(sleep_session['levels']['summary']['light']['thirtyDayAvgMinutes'])
        #             sleep_daily_dict['rem_count'].append(sleep_session['levels']['summary']['rem']['count'])
        #             sleep_daily_dict['rem_minutes'].append(sleep_session['levels']['summary']['rem']['minutes'])
        #             sleep_daily_dict['rem_thirtyDayAvgMinutes'].append(sleep_session['levels']['summary']['rem']['thirtyDayAvgMinutes'])
        #             sleep_daily_dict['wake_count'].append(sleep_session['levels']['summary']['wake']['count'])
        #             sleep_daily_dict['wake_minutes'].append(sleep_session['levels']['summary']['wake']['minutes'])
        #             sleep_daily_dict['wake_thirtyDayAvgMinutes'].append(sleep_session['levels']['summary']['wake']['thirtyDayAvgMinutes'])
        #             sleep_daily_dict['asleep_count'].append(np.nan)
        #             sleep_daily_dict['asleep_minutes'].append(np.nan)
        #             sleep_daily_dict['awake_count'].append(np.nan)
        #             sleep_daily_dict['awake_minutes'].append(np.nan)
        #             sleep_daily_dict['restless_count'].append(np.nan)
        #             sleep_daily_dict['restless_minutes'].append(np.nan)
        #         except KeyError:
        #             sleep_daily_dict['deep_count'].append(np.nan)
        #             sleep_daily_dict['deep_minutes'].append(np.nan)
        #             sleep_daily_dict['deep_thirtyDayAvgMinutes'].append(np.nan)
        #             sleep_daily_dict['light_count'].append(np.nan)
        #             sleep_daily_dict['light_minutes'].append(np.nan)
        #             sleep_daily_dict['light_thirtyDayAvgMinutes'].append(np.nan)
        #             sleep_daily_dict['rem_count'].append(np.nan)
        #             sleep_daily_dict['rem_minutes'].append(np.nan)
        #             sleep_daily_dict['rem_thirtyDayAvgMinutes'].append(np.nan)
        #             sleep_daily_dict['wake_count'].append(np.nan)
        #             sleep_daily_dict['wake_minutes'].append(np.nan)
        #             sleep_daily_dict['wake_thirtyDayAvgMinutes'].append(np.nan)
        #             sleep_daily_dict['asleep_count'].append(sleep_session['levels']['summary']['asleep']['count'])
        #             sleep_daily_dict['asleep_minutes'].append(sleep_session['levels']['summary']['asleep']['minutes'])
        #             sleep_daily_dict['awake_count'].append(sleep_session['levels']['summary']['awake']['count'])
        #             sleep_daily_dict['awake_minutes'].append(sleep_session['levels']['summary']['awake']['minutes'])
        #             sleep_daily_dict['restless_count'].append(sleep_session['levels']['summary']['restless']['count'])
        #             sleep_daily_dict['restless_minutes'].append(sleep_session['levels']['summary']['restless']['minutes'])
        # # import pickle
        # # with open('data/intraday_dict.pickle', 'wb') as handle:
        # #     pickle.dump(intraday_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # # with open('data/intraday_dict.pickle', 'rb') as handle:
        # #     intraday_dict = pickle.load(handle)

        # # # # would need to correct better later
        # # # too_long = len(intraday_dict['time'])-len(intraday_dict['heart'])
        # # # del intraday_dict['date'][-too_long:]
        # # # del intraday_dict['time'][-too_long:]

        # # intraday_df = pd.DataFrame(intraday_dict)
        # # intraday_df.to_csv('data/fitbit_intraday.csv')

        # day_df = pd.DataFrame.from_dict(day_dict)
        # day_df.to_csv('data/fitbit_day.csv')
        # spo2_df = pd.DataFrame.from_dict(spo2_dict)
        # spo2_df.to_csv('data/fitbit_spo2.csv')
        # hrv_df = pd.DataFrame.from_dict(hrv_dict)
        # hrv_df.to_csv('data/fitbit_hrv.csv')
        # activities_df = pd.DataFrame.from_dict(activities_dict)
        # activities_df.to_csv('data/fitbit_activities.csv')
        # sleep_daily_df = pd.DataFrame.from_dict(sleep_daily_dict)
        # sleep_daily_df.to_csv('data/fitbit_sleep_daily.csv')
        # sleep_intrad_df = pd.DataFrame.from_dict(sleep_intrad_dict)
        # sleep_intrad_df.to_csv('data/fitbit_sleep_intrad.csv')

        # Get Active Zone Minutes as as Time Series
        azm_dict = {
            'date': [],
            'fatBurnActiveZoneMinutes': [],
            'cardioActiveZoneMinutes': [],
            'activeZoneMinutes': []
        }
        azm_ts = self.client.time_series('activities/active-zone-minutes', period='1m')
        for day_data in azm_ts['activities-active-zone-minutes']:
            azm_dict['date'].append(day_data['dateTime'])
            for key in day_data['value'].keys():
                if key not in azm_dict:
                    print("oe")
            for key in azm_dict.keys():
                if key =='date': continue
                try:
                    azm_dict[key].append(day_data['value'][key])
                except KeyError:
                    azm_dict[key].append(np.nan)
        # Same intraday (does not work but I think it is useless to have this precise)
        # azm_ts_intrad = self.client.intraday_time_series('activities/active-zone-minutes', base_date=date2)
        azm_df = pd.DataFrame.from_dict(azm_dict)
        azm_df.to_csv('data/fitbit_azm.csv')

        # # Get Activity Log List TODO: need to save data
        # # activities list -> useless
        # # activities_list = self.client.activities_list()
        # activity_stats = self.client.activity_stats()['lifetime']['total']
        # # stats already contain recent activities
        # recent_activities = self.client.recent_activities()
        # favorite_activities = self.client.favorite_activities()
        # frequent_activities = self.client.frequent_activities()
        # goals = activities['goals']

        # sleep = self.client.sleep(date=datetime.date(2023, 10, 22)) # same as get_sleep for datetime.date.today() or datetime.date(year, month, day)
        # # need to put morning after date
        # # time series: sleep/minutesAsleep sleep/timeInBed
        # # more on sleep at https://dev.fitbit.com/build/reference/web-api/sleep/
        # # sleep_ts = self.client.time_series('sleep', period='1d')

        # # base-date: The range start date, in the format yyyy-MM-dd or today.
        # # end-date: The end date of the range.
        # # date: The end date of the period specified in the format yyyy-MM-dd or today.
        # # period: The range for which data will be returned. Options are 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y

        # date_steps_list = [(dateutil.parser.parse(date_steps_dict['dateTime']), int(date_steps_dict['value']))
        #       for date_steps_dict in steps_ts['activities-steps']]

        # # convert to data frame
        # date_steps = pd.DataFrame(date_steps_list, columns=('Date', 'Steps'))

        # # save to csv
        # date_steps.to_csv('data/daily_steps.csv', index=None, encoding='utf-8')

        # # example: minutesSedentary
        # activity_ts = self.client.time_series('activities/minutesSedentary', period='1w')
        # date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
        #             for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        # minutesSedentary = pd.DataFrame(date_act_list, columns=('Date', 'minutesSedentary'))
        # minutesSedentary.to_csv('data/minutesSedentary.csv', index=None, encoding='utf-8')

        # # example: minutesLightlyActive
        # activity_ts = self.client.time_series('activities/minutesLightlyActive', period='1w')
        # date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
        #             for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        # minutesLightlyActive = pd.DataFrame(date_act_list, columns=('Date', 'minutesLightlyActive'))
        # minutesLightlyActive.to_csv('data/minutesLightlyActive.csv', index=None, encoding='utf-8')

        # # activities/minutesFairlyActive
        # activity_ts = self.client.time_series('activities/minutesFairlyActive', period='1w')
        # date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
        #             for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        # minutesFairlyActive = pd.DataFrame(date_act_list, columns=('Date', 'minutesFairlyActive'))
        # minutesFairlyActive.to_csv('data/minutesFairlyActive.csv', index=None, encoding='utf-8')

        # # activities/minutesVeryActive
        # activity_ts = self.client.time_series('activities/minutesVeryActive', period='1w')
        # date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
        #             for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        # minutesVeryActive = pd.DataFrame(date_act_list, columns=('Date', 'minutesVeryActive'))
        # minutesVeryActive.to_csv('data/minutesVeryActive.csv', index=None, encoding='utf-8')

        # # Also weight, BMI, body-fat

        # # Daily Sleep Log in Minutes
        # sleep_ts = self.client.time_series('sleep/minutesAsleep', period='1w')
        # date_sleep_list = [(dateutil.parser.parse(date_sleep_dict['dateTime']), int(date_sleep_dict['value']))
        #       for date_sleep_dict in sleep_ts['sleep-minutesAsleep']]
        # date_sleep = pd.DataFrame(date_sleep_list, columns=('Date', 'Sleep'))
        # date_sleep['Hours'] = round((date_sleep.Sleep / 60), 2)
        # # save to csv
        # date_sleep.to_csv('data/daily_sleep.csv', index=None, encoding='utf-8')

        # # Daily InBed Log in Minutes
        # inbed_ts = self.client.time_series('sleep/timeInBed', period='1w')
        # date_inbed_list = [(dateutil.parser.parse(date_sleep_dict['dateTime']), int(date_sleep_dict['value']))
        #       for date_sleep_dict in inbed_ts['sleep-timeInBed']]
        # date_inbed = pd.DataFrame(date_inbed_list, columns=('Date', 'InBed'))
        # # save to csv
        # date_inbed.to_csv('data/daily_inbed.csv', index=None, encoding='utf-8')

        # # Steps Per 15min via Intraday API
        # # get all Steps stats for a single date
        # # self.fitbit_intraday_steps(today)
        # self.fitbit_multidates_steps(dates_list)

        # # Download Daily Detailed Sleep Log (TODO: need fixes)
        # sleep_daily = [self.client.sleep(date) for date in dates_list]
        # # check raw log of previous day
        # # sleep_daily[-2]
        # # sleep minutes
        # # sleep_minutes = [sleep_entry['summary']['totalMinutesAsleep'] for sleep_entry in sleep_daily]
        # # in-bed minutes
        # # inbed_minutes = [sleep_entry['summary']['totalTimeInBed'] for sleep_entry in sleep_daily]
        # # sleep_minutes[-3]
        # # date_sleep = pd.DataFrame({'Date': dates_list, 'Sleep': sleep_minutes, 'InBed': inbed_minutes})
        # # in bed minutes
        # # inbed_minutes = [sleep_entry['summary']['totalTimeInBed'] for sleep_entry in sleep_daily]
        # # inbed_minutes[-3]
        # # date_inbed = pd.DataFrame({'Date': dates_list, 'InBed': inbed_minutes})
        # # save to csv
        # # date_inbed.to_csv('data/daily_inbed.csv', index=None, encoding='utf-8')
        # # date_sleep[date_sleep.Sleep > 0].plot(x='Date', y="Sleep")
        # # date_inbed[date_inbed.InBed > 0].plot(x='Date', y="InBed")

        # TODO: Download Daily Resting HR and Other HR Zone Data
        # hr_ts = auth2_client.time_series('activities/heart', period='30d')
        # hr_ts['activities-heart'][-7] # check  from a week ago
        # resting hr
        # hr_ts['activities-heart'][-7]['value']['restingHeartRate'] # check from a week ago
        # Out of Range data
        # hr_ts['activities-heart'][-7]['value']['heartRateZones']\
        #        ['name' == 'Out of Range'] # check  from a week ago
        # Out of Range data = Calories Out
        #hr_ts['activities-heart'][-7]['value']['heartRateZones']\
        #        ['name' == 'Out of Range']['caloriesOut']
        # Fat Burn
        # Cardio
        # Peak
        # trying to parse into a list with date and resting heart rate
        #date_hr_list = [(dateutil.parser.parse(date_hr_dict['dateTime']), \
        #                (date_hr_dict['value')) \
        #                for date_hr_dict in hr_ts['activities-heart']]
        # type(date_hr_list)
        # type(date_hr_list[-1])

        # # Full Day Record of Heart Rate
        # # get multiple date HR data
        # def fitbit_multidates_hr(datelist):
        #     for i in datelist[:]:
        #         self.fitbit_HR_stats(i)
        #         # add a 5 second daily
        #         # time.sleep(5)
        # # today's hr data
        # # fitbit_HR_stats(today)
        # # yesterday's data
        # # fitbit_HR_stats(yesterday)
        # # get data for multiple days
        # fitbit_multidates_hr(dates_list)

        print("oe")

    def get_data(self):
        # Get Today and Yesterday Dates in FitBit Ready Formats
        yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"))
        yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        today = str(datetime.datetime.now().strftime("%Y-%m-%d"))

        # list of dates to check
        dates_list = []
        date1 = '2023-10-22' # Got Fitbit Device 2018-04-17 or since last data update
        date2 = today
        start = datetime.datetime.strptime(date1, '%Y-%m-%d')
        end = datetime.datetime.strptime(date2, '%Y-%m-%d')
        step = datetime.timedelta(days=1)

        while start <= end:
            dates_list.append(start.date().strftime("%Y-%m-%d"))
            start += step


        # download daily steps data
        # Get Steps Data in JSON from Last Year
        try:
            steps_ts = self.client.time_series('activities/steps', period='1d')
        except fitbit.exceptions.HTTPUnauthorized:
            self.refresh_token()
            steps_ts = self.client.time_series('activities/steps', period='1d')

        # Get Active Zone Minutes as as Time Series
        azm_ts = self.client.time_series('activities/active-zone-minutes', period='1w')
        # Same intraday (does not work but I think it is useless to have this precise)
        # azm_ts_intrad = self.client.intraday_time_series('activities/active-zone-minutes', base_date=date2)

        # Get Activity Log List
        activities = self.client.activities(date = date2)
        # activities list -> useless
        # activities_list = self.client.activities_list()
        activity_stats = self.client.activity_stats()
        # stats already contain recent activities
        recent_activities = self.client.recent_activities()

        # Get activities time series
        # activityCalories	tracker/activityCalories
        # calories	tracker/calories
        # caloriesBMR	N/A
        # distance	tracker/distance
        # elevation	tracker/elevation
        # floors	tracker/floors
        # minutesSedentary	tracker/minutesSedentary
        # minutesLightlyActive	tracker/minutesLightlyActive
        # minutesFairlyActive	tracker/minutesFairlyActive
        # minutesVeryActive	tracker/minutesVeryActive
        # steps	tracker/steps
        steps = self.client.time_series('activities/steps', period="1d")
        minutesVeryActive = self.client.time_series('activities/minutesVeryActive', period="1d")
        minutesFairlyActive = self.client.time_series('activities/minutesFairlyActive', period="1d")
        minutesLightlyActive = self.client.time_series('activities/minutesLightlyActive', period="1d")
        minutesSedentary = self.client.time_series('activities/minutesSedentary', period="1d")
        elevation = self.client.time_series('activities/elevation', period="1d")
        floors = self.client.time_series('activities/floors', period="1d")
        distance = self.client.time_series('activities/distance', period="1d")
        calories = self.client.time_series('activities/calories', period="1d")
        activityCalories = self.client.time_series('activities/activityCalories', period="1d")

        steps_intrad = self.client.intraday_time_series('activities/steps', base_date=date2)
        minutesVeryActive_intrad = self.client.intraday_time_series('activities/minutesVeryActive', base_date=date2)
        minutesFairlyActive_intrad = self.client.intraday_time_series('activities/minutesFairlyActive', base_date=date2)
        minutesLightlyActive_intrad = self.client.intraday_time_series('activities/minutesLightlyActive', base_date=date2)
        minutesSedentary_intrad = self.client.intraday_time_series('activities/minutesSedentary', base_date=date2)
        elevation_intrad = self.client.intraday_time_series('activities/elevation', base_date=date2)
        floors_intrad = self.client.intraday_time_series('activities/floors', base_date=date2)
        distance_intrad = self.client.intraday_time_series('activities/distance', base_date=date2)
        calories_intrad = self.client.intraday_time_series('activities/calories', base_date=date2)
        activityCalories_intrad = self.client.intraday_time_series('activities/activityCalories', base_date=date2)

        # act_ts = self.client.time_series('activities')

        headers = {
            'Authorization': 'Bearer ' + self.__access_token
        }
        br_date = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/br/date/2023-10-23.json", headers = headers).json()
        br_date_intrad = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/br/date/2023-10-23/all.json", headers = headers).json()

        vo2_date = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/cardioscore/date/2023-10-23.json", headers = headers).json()

        hr = self.client.time_series('activities/heart', period="1w")
        hr_intrad = self.client.intraday_time_series('activities/heart', base_date=date2)

        hrv = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/hrv/date/2023-10-23.json", headers = headers).json()
        hrv_intrad = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/hrv/date/2023-10-23/all.json", headers = headers).json()

        sleep = self.client.sleep(date=datetime.date(2023, 10, 22)) # same as get_sleep for datetime.date.today() or datetime.date(year, month, day)
        # need to put morning after date
        # time series: sleep/minutesAsleep sleep/timeInBed
        # more on sleep at https://dev.fitbit.com/build/reference/web-api/sleep/
        # sleep_ts = self.client.time_series('sleep', period='1d')

        spO2_ts = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/spo2/date/2023-10-23.json", headers = headers)
        spO2_intrad = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/spo2/date/2023-10-23/all.json", headers = headers)

        temp_ts = requests.get(f"https://api.fitbit.com/1/user/{self.__user_id}/temp/skin/date/2023-10-23.json", headers = headers)

        # base-date: The range start date, in the format yyyy-MM-dd or today.
        # end-date: The end date of the range.
        # date: The end date of the period specified in the format yyyy-MM-dd or today.
        # period: The range for which data will be returned. Options are 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y

        date_steps_list = [(dateutil.parser.parse(date_steps_dict['dateTime']), int(date_steps_dict['value']))
              for date_steps_dict in steps_ts['activities-steps']]

        # convert to data frame
        date_steps = pd.DataFrame(date_steps_list, columns=('Date', 'Steps'))

        # save to csv
        date_steps.to_csv('data/daily_steps.csv', index=None, encoding='utf-8')

        # see more options for https://dev.fitbit.com/build/reference/web-api/activity/#activity-time-series
        # activities/calories
        # activities/caloriesBMR
        # activities/steps
        # activities/distance
        # activities/floors
        # activities/elevation
        # activities/minutesSedentary
        # activities/minutesLightlyActive
        # activities/minutesFairlyActive
        # activities/minutesVeryActive
        # activities/activityCalories

        # example: minutesSedentary
        activity_ts = self.client.time_series('activities/minutesSedentary', period='1w')
        date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
                    for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        minutesSedentary = pd.DataFrame(date_act_list, columns=('Date', 'minutesSedentary'))
        minutesSedentary.to_csv('data/minutesSedentary.csv', index=None, encoding='utf-8')

        # example: minutesLightlyActive
        activity_ts = self.client.time_series('activities/minutesLightlyActive', period='1w')
        date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
                    for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        minutesLightlyActive = pd.DataFrame(date_act_list, columns=('Date', 'minutesLightlyActive'))
        minutesLightlyActive.to_csv('data/minutesLightlyActive.csv', index=None, encoding='utf-8')

        # activities/minutesFairlyActive
        activity_ts = self.client.time_series('activities/minutesFairlyActive', period='1w')
        date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
                    for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        minutesFairlyActive = pd.DataFrame(date_act_list, columns=('Date', 'minutesFairlyActive'))
        minutesFairlyActive.to_csv('data/minutesFairlyActive.csv', index=None, encoding='utf-8')

        # activities/minutesVeryActive
        activity_ts = self.client.time_series('activities/minutesVeryActive', period='1w')
        date_act_list = [(dateutil.parser.parse(date_act_dict['dateTime']), int(date_act_dict['value']))
                    for date_act_dict in activity_ts[list(activity_ts.keys())[0]]]
        minutesVeryActive = pd.DataFrame(date_act_list, columns=('Date', 'minutesVeryActive'))
        minutesVeryActive.to_csv('data/minutesVeryActive.csv', index=None, encoding='utf-8')

        # Also weight, BMI, body-fat

        # Daily Sleep Log in Minutes
        sleep_ts = self.client.time_series('sleep/minutesAsleep', period='1w')
        date_sleep_list = [(dateutil.parser.parse(date_sleep_dict['dateTime']), int(date_sleep_dict['value']))
              for date_sleep_dict in sleep_ts['sleep-minutesAsleep']]
        date_sleep = pd.DataFrame(date_sleep_list, columns=('Date', 'Sleep'))
        date_sleep['Hours'] = round((date_sleep.Sleep / 60), 2)
        # save to csv
        date_sleep.to_csv('data/daily_sleep.csv', index=None, encoding='utf-8')

        # Daily InBed Log in Minutes
        inbed_ts = self.client.time_series('sleep/timeInBed', period='1w')
        date_inbed_list = [(dateutil.parser.parse(date_sleep_dict['dateTime']), int(date_sleep_dict['value']))
              for date_sleep_dict in inbed_ts['sleep-timeInBed']]
        date_inbed = pd.DataFrame(date_inbed_list, columns=('Date', 'InBed'))
        # save to csv
        date_inbed.to_csv('data/daily_inbed.csv', index=None, encoding='utf-8')

        # Steps Per 15min via Intraday API
        # get all Steps stats for a single date
        # self.fitbit_intraday_steps(today)
        self.fitbit_multidates_steps(dates_list)

        # Download Daily Detailed Sleep Log (TODO: need fixes)
        # sleep_daily = [self.client.sleep(date) for date in dates_list]
        # check raw log of previous day
        # sleep_daily[-2]
        # sleep minutes
        # sleep_minutes = [sleep_entry['summary']['totalMinutesAsleep'] for sleep_entry in sleep_daily]
        # in-bed minutes
        # inbed_minutes = [sleep_entry['summary']['totalTimeInBed'] for sleep_entry in sleep_daily]
        # sleep_minutes[-3]
        # date_sleep = pd.DataFrame({'Date': dates_list, 'Sleep': sleep_minutes, 'InBed': inbed_minutes})
        # in bed minutes
        # inbed_minutes = [sleep_entry['summary']['totalTimeInBed'] for sleep_entry in sleep_daily]
        # inbed_minutes[-3]
        # date_inbed = pd.DataFrame({'Date': dates_list, 'InBed': inbed_minutes})
        # save to csv
        # date_inbed.to_csv('data/daily_inbed.csv', index=None, encoding='utf-8')
        # date_sleep[date_sleep.Sleep > 0].plot(x='Date', y="Sleep")
        # date_inbed[date_inbed.InBed > 0].plot(x='Date', y="InBed")

        # TODO: Download Daily Resting HR and Other HR Zone Data
        # hr_ts = auth2_client.time_series('activities/heart', period='30d')
        # hr_ts['activities-heart'][-7] # check  from a week ago
        # resting hr
        # hr_ts['activities-heart'][-7]['value']['restingHeartRate'] # check from a week ago
        # Out of Range data
        # hr_ts['activities-heart'][-7]['value']['heartRateZones']\
        #        ['name' == 'Out of Range'] # check  from a week ago
        # Out of Range data = Calories Out
        #hr_ts['activities-heart'][-7]['value']['heartRateZones']\
        #        ['name' == 'Out of Range']['caloriesOut'] 
        # Fat Burn
        # Cardio
        # Peak
        # trying to parse into a list with date and resting heart rate
        #date_hr_list = [(dateutil.parser.parse(date_hr_dict['dateTime']), \
        #                (date_hr_dict['value')) \
        #                for date_hr_dict in hr_ts['activities-heart']]
        # type(date_hr_list)
        # type(date_hr_list[-1])

        # # Full Day Record of Heart Rate
        # # get multiple date HR data
        # def fitbit_multidates_hr(datelist):
        #     for i in datelist[:]:
        #         self.fitbit_HR_stats(i)
        #         # add a 5 second daily
        #         # time.sleep(5)
        # # today's hr data
        # # fitbit_HR_stats(today)
        # # yesterday's data
        # # fitbit_HR_stats(yesterday)
        # # get data for multiple days
        # fitbit_multidates_hr(dates_list)
        print("oe")


    # get all HR stats for a single date
    def fitbit_HR_stats(self, date):
        fitbit_intra_HR = self.client.intraday_time_series('activities/heart', base_date=date, detail_level='1sec')
        time_list = []
        val_list = []
        for i in fitbit_intra_HR['activities-heart-intraday']['dataset']:
            val_list.append(i['value'])
            time_list.append(i['time'])
        heartdf = pd.DataFrame({'Heart_Rate':val_list,'Time':time_list})
        # add date column
        heartdf['Date'] = date
        # create csv
        heartdf.to_csv('data/hr/heart'+ \
                date+'.csv', \
                columns=['Date', 'Time','Heart_Rate'], header=True, \
                index = False)
        print("Generated CSV for %s" % date)


    def fitbit_intraday_steps(self, date):
        fitbit_intra_steps = self.client.intraday_time_series('activities/steps', base_date=date, detail_level='15min')
        time_list = []
        val_list = []
        for i in fitbit_intra_steps['activities-steps-intraday']['dataset']:
            val_list.append(i['value'])
            time_list.append(i['time'])
        heartdf = pd.DataFrame({'Steps':val_list,'Time':time_list})
        # add date column
        heartdf['Date'] = date
        # create csv
        heartdf.to_csv('data/steps/steps'+ \
                date+'.csv', \
                columns=['Date', 'Time','Steps'], header=True, \
                index = False)
        print("Generated Steps CSV for %s" % date)

    # get multiple date HR data
    def fitbit_multidates_steps(self, datelist):
        for i in datelist[:]:
            self.fitbit_intraday_steps(i)
            # add a 5 second daily
            # time.sleep(5)

def fill_dic(data, t):
    dic = []
    i=0
    for d in data:
        while not d['time'] == t[i]:
            dic.append(None)
            i+=1
        dic.append(d['value'])
        i+=1
    if i<len(t):
        dic.extend([None for _ in range(len(t)-i)])
    return dic
