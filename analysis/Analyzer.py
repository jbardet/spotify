from Configs.Parser import Parser
from Credentials.Credentials import Credentials

from RescueWakaTime.RescueWakaTime import RescueWakaTime
from Todoist.Todoist import Todoist
from Timer.Timer import Timer
from Spotify.Radar import Radar
# from Calendar.Calendar import Calendar
from Fitbit.Fitbit import Fitbit
# from .LastFM import LastFM
from Configs.Parser import Parser

class Analyzer:
    """
    Class that saves data from the different APIs and generates a weekly report
    """

    def __init__(self):
        """
        Initialize the class by first setting up the different classes for the
        different APIs
        """
        self.rw_time = RescueWakaTime()
        self.todoist = Todoist()
        self.fitbit = Fitbit()

    def weekly_review(self):
        """
        First fetch and save data from the different APIs and then generate the
        weekly report
        """
        self.save_data()
        self.generate_weekly_report()

    def generate_weekly_report(self):
        """
        Generates a nice report of the week
        """
        # TODO: in tableau or D3.js
        pass

    def save_data(self):
        """
        Save data from the APIs to local CSV files
        """
        # self.rw_time.save_data()
        # self.todoist.save_data()
        self.fitbit.save_data()