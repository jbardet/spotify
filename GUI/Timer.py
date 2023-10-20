import time
import tkinter as tk
from tkinter import StringVar, Entry, Label, Button
from tkinter import messagebox

from helpers import add_website_link

class Timer():
    """
    Class to handle the POMODORO timer but also the links to the stretching
    websites
    """
    def __init__(self, window: tk.Frame) -> None:
        """
        Initialize the frame with the timer and the links

        :param window: the window frame where to place the timer and the links
        :type window: tk.Frame
        """
        self.window = window
        self.add_timer()
        self.add_links()

    def submit(self):
        """
        Start the timer
        """
        try:
            # the input provided by the user is
            # stored in here :temp
            temp = int(self.hour.get())*3600 + int(self.minute.get())*60 + int(self.second.get())
        except:
            print("Please input the right value")
        while temp >-1:
            mins,secs = divmod(temp,60)

            # Converting the input entered in mins or secs to hours,
            # mins ,secs(input = 110 min --> 120*60 = 6600 => 1hr :
            # 50min: 0sec)
            hours=0
            if mins >60:
                hours, mins = divmod(mins, 60)

            # using format () method to store the value up to
            # two decimal places
            self.hour.set("{0:2d}".format(hours))
            self.minute.set("{0:2d}".format(mins))
            self.second.set("{0:2d}".format(secs))

            # updating the GUI window after decrementing the
            # temp value every time
            self.window.update()
            time.sleep(1)

            # when temp value = 0; then a messagebox pop's up
            # with a message:"Time's up"
            if (temp == 0):
                messagebox.showinfo("Time Countdown", "Time's up ")

            # after every one sec the value of temp will be decremented
            # by one
            temp -= 1


    def add_timer(self) -> None:
        """
        Add a timer in the upper right part of the GUI
        """
        # Declaration of variables
        self.hour=StringVar()
        self.minute=StringVar()
        self.second=StringVar()

        # Setting the default value as 50 minutes (preferred time for a pomodoro)
        self.hour.set("00")
        self.minute.set("50")
        self.second.set("00")

        # Set a label to explain the timer
        timer_label = Label(self.window, text="POMODORO: ", font=("Arial",18,""))
        timer_label.pack(side = tk.TOP)

        # Use of Entry class to take input from the user
        hourEntry= Entry(self.window, width=3, font=("Arial",18,""),
                         textvariable=self.hour)
        # place it in upper right corner
        hourEntry.pack(side = tk.LEFT)

        minuteEntry= Entry(self.window, width=3, font=("Arial",18,""),
                           textvariable=self.minute)
        minuteEntry.pack(side = tk.LEFT)

        secondEntry= Entry(self.window, width=3, font=("Arial",18,""),
                           textvariable=self.second)
        secondEntry.pack(side = tk.LEFT)

        # Button widget to start the countdown
        btn = Button(self.window, text='Set Time Countdown', font=("Arial",18),
                    command= self.submit)
        btn.pack(side = tk.LEFT)

    def add_links(self) -> None:
        """
        Add links to the stretching websites on the GUI
        """

        texts = ["healthline", "verywellfit"]
        urls = [
            "https://www.healthline.com/health/deskercise",
            "https://www.verywellfit.com/best-stretches-for-office-workers-1231153"
        ]
        font = ('Aerial 12')
        side = "bottom"

        add_website_link(self.window, urls[0], texts[0], font, side)
        add_website_link(self.window, urls[1], texts[1], font, side)
