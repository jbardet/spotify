import time
import os
import sys
import sched
from typing import Callable

class Monitor():
    """
    Class that handles the monitoring of the song for the plot. It needs to know
    how long the song is and when it is finished to update the plot
    """
    def __init__(self, time_song: int, callback: Callable):
        """
        Initialize the Monitor class with the timer for how long the song is

        :param time_song: how long before the song ends in seconds
        :type time_song: int
        :param callback: the function to update the graph when the song change
        :type callback: Callable
        """
        self.running = True
        self.callback = callback
        self.schedule = sched.scheduler(time.time, time.sleep)
        self.offset = 5
        self.time_song = time_song - self.offset
        self.start()

    def start(self):
        """
        Start the timer
        """
        self.running = True
        self.event = self.schedule.enter(self.time_song,
                                         1,
                                         self.callback,
                                         (self.schedule,))

    def stop(self):
        """
        Stop the timer
        """
        self.running = False
        self.schedule.cancel()

    def new_song(self, time_song: int):
        """
        Update the monitor with a new song and its time

        :param time_song: how long before the song ends in seconds
        :type time_song: int
        """
        try:
            self.schedule.cancel(self.event)
        except ValueError:
            #the event has terminated by itself
            pass
        self.time_song = time_song - self.offset
        self.event = self.schedule.enter(self.time_song,
                                         1,
                                         self.callback,
                                         (self.schedule,))

    # def update(self, schedule=None):
    #     """
    #     :param schedule: _description_, defaults to None
    #     :type schedule: _type_, optional
    #     """
    #     self.callback()


    # def enter(self, time_song: int):
    #     """
    #     Enter a new song and its time
    #     :param time_song: how long before the song ends in seconds
    #     :type time_song: int
    #     """
    #     self.time_song = time_song
    #     self.start()
