import configparser
import os
import logging
import numpy as np
from typing import Union, Dict, Callable, Optional, Any, List
from enum import unique, auto, IntEnum, Enum
import sys
from pathlib import Path

class Parser():
    """
    Gets all the informations from config file with optional and needed options
    """

    # The configs file lies in the same folder as this script
    __configs_file = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                  '..',
                                                  'config.txt'))

    @staticmethod
    def initialize():
        """
        Static method to initialize the different config parameters
        """
        Parser.configs = configparser.RawConfigParser()
        Parser.configs.read(Parser.__configs_file)

        # If the configparser is empty it means the Config file has not been found
        if len(Parser.configs._sections) == 0:
            raise FileNotFoundError(Parser.__configs_file)

        Parser.__tk_theme = Parser.configs.get("GUI", "tk_theme")
        Parser.__plt_theme = Parser.configs.get("GUI", "plt_theme")

        Parser.__device_id = Parser.configs.get("Spotify", "device_id")

        Parser.__goal = Parser.configs.get("Timer", "goal")
        Parser.__pomodoro = Parser.configs.get("Timer", "pomodoro")

        Parser.__timer_data_file = Parser.configs.get("Drive", "timer_data_file")
        Parser.__offline_data_file = Parser.configs.get("Drive", "offline_data_file")

        # Fitbit
        Parser.__fitbit_intraday = Parser.configs.get("Fitbit", "fitbit_intraday")
        Parser.__fitbit_day = Parser.configs.get("Fitbit", "fitbit_day")
        Parser.__fitbit_spo2 = Parser.configs.get("Fitbit", "fitbit_spo2")
        Parser.__fitbit_hrv = Parser.configs.get("Fitbit", "fitbit_hrv")
        Parser.__fitbit_sleep_intrad = Parser.configs.get("Fitbit", "fitbit_sleep_intrad")
        Parser.__fitbit_sleep_day = Parser.configs.get("Fitbit", "fitbit_sleep_day")

    @staticmethod
    def get_tk_theme() -> str:
        """
        Get the Tkinter theme

        :return: the name of theme
        :rtype: str
        """
        return Parser.__tk_theme

    @staticmethod
    def get_plt_theme() -> str:
        """
        Get the matplotlib theme

        :return: the name of theme
        :rtype: str
        """
        return Parser.__plt_theme

    @staticmethod
    def get_device_id() -> str:
        """
        Get the Device ID for Spotify

        :return: the id of the device
        :rtype: str
        """
        return Parser.__device_id

    @staticmethod
    def get_goal() -> str:
        """
        Get the goal of the timer

        :return: the goal of the timer
        :rtype: str
        """
        return Parser.__goal

    @staticmethod
    def get_pomodoro() -> str:
        """
        Get the pomodoro time the suer desires in minutes

        :return: the pomodoro time
        :rtype: str
        """
        return Parser.__pomodoro

    @staticmethod
    def get_timer_data_file() -> str:
        """
        Get the Timer data filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__timer_data_file

    @staticmethod
    def get_offline_work_file() -> str:
        """
        Get the Offline work filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__offline_data_file

    @staticmethod
    def get_fitbit_intraday() -> str:
        """
        Get the Fitbit Intraday filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__fitbit_intraday

    @staticmethod
    def get_fitbit_day() -> str:
        """
        Get the Fitbit Day filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__fitbit_day

    @staticmethod
    def get_fitbit_spo2() -> str:
        """
        Get the Fitbit SpO2 filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__fitbit_spo2

    @staticmethod
    def get_fitbit_hrv() -> str:
        """
        Get the Fitbit HRV filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__fitbit_hrv

    @staticmethod
    def get_fitbit_sleep_intrad() -> str:
        """
        Get the Fitbit Sleep Intraday filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__fitbit_sleep_intrad

    @staticmethod
    def get_fitbit_sleep_day() -> str:
        """
        Get the Fitbit Sleep Day filename

        :return: the name of the file
        :rtype: str
        """
        return Parser.__fitbit_sleep_day
