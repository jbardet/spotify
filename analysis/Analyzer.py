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
    def __init__(self):
        self.rw_time = RescueWakaTime()
        self.todoist = Todoist()
        self.fitbit = Fitbit()

    def weekly_review(self):
        # self.rw_time = RescueWakaTime(rescue_cr, waka_cr, self.left_frame)
        # self.rw_time.save_data()
        # self.todoist = Todoist(self.upright_frame)
        # self.todoist.save_data(last_save)
        # self.radar = Radar(spotify_cr, db_cr, self.middle_frame)
        # self.radar.save_data()
        # self.fitbit = Fitbit(fitbit_cr)
        # self.fitbit.save_data()
        # self.lastfm = LastFM(lastfm_cr)
        # self.lastfm.save_data()

        self.save_data()

    def generate_weekly_report(self):
        pass

    def save_data(self):
        # self.rw_time.save_data()
        # self.todoist.save_data()
        self.fitbit.save_data()