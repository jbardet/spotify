import tkinter as tk
from typing import List
import datetime
import pickle
import datetime
import os.path
from todoist_api_python.api import Task

from helpers import add_website_link

class Todoist():
    def __init__(self, key: str,  window: tk.Frame) -> None:
        """
        Initialize the Todoist class with the tasks from Todoist

        :param key: the key to access Todoist's API
        :type key: str
        :param window: the window frame where to place the tasks list
        :type window: tk.Frame
        """
        self.__key = key
        self.window = window

        self.tasks = self.get_tasks()

    def get_tasks(self) -> List[Task]:
        """
        Get the tasks that are in the section Work in Todoist and that are
        due in the next 2 days

        :return: the list of tasks to do
        :rtype: List[Task]
        """
        # api = TodoistAPI(self.__key)
        # today = datetime.datetime.now()
        # after_tomorrow = f"{today.month}/{today.day+2}"
        # try:
        #     tasks = api.get_tasks(
        #         filter = f"due before: {after_tomorrow} & #Work & /Work TODO")
        # except Exception as error:
        #     print(error)
        # with open("tasks.pkl", "wb") as file:
        #     pickle.dump(tasks, file)
        with open("tasks.pkl", "rb") as file:
            tasks = pickle.load(file)
        return tasks

    def add_tasks(self) -> None:
        """
        Add Todoist tasks to the right part of the main GUI

        We add:
        - a link to Todoist's website to handle the tasks shown and update them
        - a list of tasks that becomes green once clicked (and completed)
        """
        self.add_website_link()
        self.add_tasks_list()

    def add_website_link(self) -> None:
        """
        Add a website link to the Todoist website to handle the tasks shown
        """
        text = "Todoist"
        url = "https://todoist.com/app/project/2313332067"
        font = ('Aerial 12')
        side = "top"
        add_website_link(self.window, url, text, font, side)

    def add_tasks_list(self):
        """
        Add the list of tasks to the right part of the main GUI and change the
        color of the task when it is clicked (and completed)
        """
        # projects -> list of length 4 wit each being a Project object
        # class attributes: dict_keys(['color', 'comment_count', 'id',
        # 'is_favorite', 'is_inbox_project', 'is_shared', 'is_team_inbox',
        # 'name', 'order', 'parent_id', 'url', 'view_style'])

        # Define the function that changes the color of the selected item
        def change_color() -> None:
            """
            Change the color of the selected item in the list of tasks
            """
            # Get the index of the selected item
            active_selection = self.tasks_listbox.curselection()

            # Change the background color of the selected item
            # if green change to red and if red change to white
            if active_selection:
                if self.tasks_listbox.itemcget(active_selection,
                                               "background") == "green":
                    self.tasks_listbox.itemconfig(active_selection,
                                                  bg=self.task_colors[active_selection[0]])
                else:
                    self.tasks_listbox.itemconfig(active_selection, bg='green')

         # Create the listbox to display the tasks
        self.tasks_listbox = tk.Listbox(self.window, bg='white',
                                        height=10, width=40, font=('Arial', 18),
                                        justify='center')
        self.tasks_listbox.pack(side = tk.TOP)
        colors = ["yellow", "blue", "orange", "red"]
        self.task_colors = []
        for i, task in enumerate(self.tasks):
            due_date = task.due.date.split("-")
            due_date = datetime.date(eval(due_date[0]),
                                     eval(due_date[1]),
                                     eval(due_date[2]))
            color = colors[task.priority-1]
            self.task_colors.append(color)
            self.tasks_listbox.insert(i,
                                      task.content+" due: "+str((due_date-datetime.date.today()).days+1))
            self.tasks_listbox.itemconfig(i, {'bg':color})

        # bind the button to the function that changes the color of the selected
        self.tasks_listbox.bind('<<ListboxSelect>>', lambda event: change_color())
