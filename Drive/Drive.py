import pandas as pd
import pygsheets
import os
import sys
from datetime import date
import googleapiclient
from typing import Dict, List, Tuple

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

    def save_data(self, name: str, dic: Dict[str, List[str]]):
        """
        Save data to spreadsheet

        :param name: the name of the spreadsheets
        :type name: str
        :param dic: the data to save
        :type dic: Dict[str, List[str]]
        """
        # open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        df_drive, wks = self.get_data(name)
        # update the first sheet with df, starting at cell B2.
        df = pd.DataFrame.from_dict(dic)
        df_save = pd.concat([df_drive, df], ignore_index=True)
        wks.set_dataframe(df_save,(0,0))

    # def load_data(self):
    #     df_drive, _ = self.get_data(self.timer_data_file)
    #     retry = True
    #     while retry:
    #         retry = False
    #         try:
    #             df_drive['time'] = pd.to_datetime(df_drive['time'])
    #             # find columns where the date is today
    #             today_work = df_drive[df_drive['time'].dt.date == date.today()]
    #             for _, row in today_work.iterrows():
    #                 self.timer_dict["event"].append(row['event'])
    #                 self.timer_dict["time"].append(row['time'])
    #         except KeyError:
    #             pass
    #         except TypeError:
    #             print("Fail to load timer data, retrying")
    #             retry = True
    #     self.timer_suppress = len(self.timer_dict["event"])

    #     df_drive, _ = self.get_data(self.offline_data_file)
    #     # find columns where the date is today
    #     retry = True
    #     while retry:
    #         retry = False
    #         try:
    #             df_drive['date'] = pd.to_datetime(df_drive['date'])
    #             today_work = df_drive[df_drive['date'].dt.date == date.today()]
    #             for _, row in today_work.iterrows():
    #                 self.offline_dict["category"].append(row['category'])
    #                 self.offline_dict["description"].append(row['description'])
    #                 self.offline_dict["start"].append(row['start'])
    #                 self.offline_dict["end"].append(row['end'])
    #                 self.offline_dict["date"].append(row['date'].date())
    #         except KeyError:
    #             pass
    #         except TypeError:
    #             print("Fail to load offline data, retrying")
    #             retry = True
    #     self.offline_suppress = len(self.offline_dict["category"])

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

    # def save_data(self):
    #     df_drive, wks = self.get_data(self.timer_data_file)
    #     df_drive.drop(df_drive.tail(self.timer_suppress).index, inplace = True)
    #     #update the first sheet with df, starting at cell B2.
    #     df = pd.DataFrame.from_dict(self.timer_dict)
    #     df_save = pd.concat([df_drive, df], ignore_index=True)
    #     wks.set_dataframe(df_save,(0,0))

    #     df_drive, wks = self.get_data(self.offline_data_file)
    #     df_drive.drop(df_drive.tail(self.offline_suppress).index, inplace = True)
    #     #update the first sheet with df, starting at cell B2.
    #     df = pd.DataFrame.from_dict(self.offline_dict)
    #     df_save = pd.concat([df_drive, df], ignore_index=True)
    #     wks.set_dataframe(df_save,(0,0))