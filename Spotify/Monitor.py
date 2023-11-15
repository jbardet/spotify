import time
import os
import sys
import sched

class Monitor():
    def __init__(self, time_song: int, callback):
        self.running = True
        self.callback = callback
        self.schedule = sched.scheduler(time.time, time.sleep)
        self.offset = 5
        self.time_song = time_song - self.offset
        self.start()

    def start(self):
        self.running = True
        self.event = self.schedule.enter(self.time_song, 1, self.update, (self.schedule,))

    def stop(self):
        self.running = False
        self.schedule.cancel()

    def new_song(self, time_song):
        try:
            self.schedule.cancel(self.event)
        except ValueError:
            #the event has terminated by itself
            pass
        self.time_song = time_song - self.offset
        self.event = self.schedule.enter(self.time_song, 1, self.update, (self.schedule,))

    def update(self, schedule=None):
        print("change_song")
        self.callback()
        # try:
        #     self.callback()
        # except AttributeError:
        #     time.sleep(20)
        #     self.callback()

    def enter(self, time_song):
        self.time_song = time_song
        self.start()
