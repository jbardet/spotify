import pandas as pd
import pygsheets
import os
import sys
from datetime import date
import googleapiclient
from typing import Dict, List, Tuple
from Configs.Parser import Parser
from datetime import datetime

class Drive():
    """
    Class to handle the google drive saving data
    """

    def __init__(self):
        """
        Initialize Google Drive with credentials
        """
        # authorization
        try:
            self.gc = pygsheets.authorize(service_file='Credentials/spotify-402405-59d8f4e06e41.json')
        except FileNotFoundError:
            self.gc = pygsheets.authorize(service_file=os.path.join(sys.path[-1],
                                                               'Credentials/spotify-402405-59d8f4e06e41.json'))
        self.offline_data = Parser.get_offline_work_file()
        self.timer_data = Parser.get_timer_data_file()


    def save_data(self, name: str, dic: Dict[str, List[str]], suppress: int = 0):
        """
        Save data to Google Drive spreadsheet

        :param name: the name of the spreadsheets
        :type name: str
        :param dic: the data to save
        :type dic: Dict[str, List[str]]
        """
        # open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        df_drive, wks = self.get_data(name)
        if suppress>0:
            df_drive.drop(df_drive.tail(suppress).index, inplace = True)
        # update the first sheet with df, starting at cell B2.
        df = pd.DataFrame.from_dict(dic)
        df_save = pd.concat([df_drive, df], ignore_index=True)
        wks.set_dataframe(df_save,(0,0))

    def save_history_data(self, data_to_save):
        self.save_data("spotify.csv", data_to_save)

    def save_liked_data(self, data_to_save):
        self.save_data("liked_songs.csv", data_to_save)

    def get_timer_data(self):
        data = self.get_data(self.timer_data)
        return data[0].columns, data[0]['time'][pd.to_datetime(data[0]['time']) == pd.Timestamp.today()].values

    def get_offline_data(self):
        data = self.get_data(self.offline_data)
        return data[0].columns, data[0]['date'][pd.to_datetime(data[0]['date']) == pd.Timestamp.today()].values

    def save_timer_data(self, timer_dict, timer_suppress):
        self.save_data(self.timer_data, timer_dict, timer_suppress)

    def save_offline_data(self, offline_dict, timer_suppress):
        self.save_data(self.offline_data, offline_dict, timer_suppress)

    def get_data(self, name: str) -> Tuple[pd.DataFrame, pygsheets.Worksheet]:
        """
        Get the data from the Google Drive spreadsheet

        :param name: the name of the file
        :type name: str
        :return: the dataframe from the file read and the worksheet
        :rtype: Tuple[pd.DataFrame, pygsheets.Worksheet]
        """
        # open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        # DO NOT FORGET TO SHARE THE SPREADSHEET
        try:
            sh = self.gc.open(name)
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
