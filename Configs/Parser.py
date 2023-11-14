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
        Parser.__goal = Parser.configs.get("Timer", "goal")
        Parser.__timer_data_file = Parser.configs.get("Drive", "timer_data_file")
        Parser.__offline_data_file = Parser.configs.get("Drive", "offline_data_file")

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
    def get_goal() -> str:
        """
        Get the goal of the timer

        :return: the goal of the timer
        :rtype: str
        """
        return Parser.__goal

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

