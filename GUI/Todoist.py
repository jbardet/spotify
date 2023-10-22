import tkinter as tk
from typing import List
import datetime
import pickle
import datetime
import os.path
import pandas as pd
import numpy as np
from todoist_api_python.api import Task
from todoist.api import TodoistAPI

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

    def get_completed_todoist_items(self, user_completed_stats):
        # create df from initial 50 completed tasks
        print("Collecting Initial 50 Completed Todoist Tasks...")
        temp_tasks_dict = (self.api.completed.get_all(limit=50))
        past_tasks = pd.DataFrame.from_dict(temp_tasks_dict['items'])
        # get the remaining items
        pager = list(range(50,user_completed_stats,50))
        for count, item in enumerate(pager):
            tmp_tasks = (self.api.completed.get_all(limit=50, offset=item))
            tmp_tasks_df = pd.DataFrame.from_dict(tmp_tasks['items'])
            past_tasks = pd.concat([past_tasks, tmp_tasks_df])
            print("Collecting Additional Todoist Tasks " + str(item) + " of " + str(user_completed_stats))
        # save to CSV
        print("...Generating CSV Export")
        past_tasks.to_csv("data/todost-raw-tasks-completed.csv", index=False)

    # get project info from Todoist API
    def get_todoist_project_name(self, project_id):
        item = self.api.projects.get_by_id(project_id)
        if item:
            try:
                return item['name']
            except:
                return item['project']['name']

    def weekly_save(self):
        self.api = TodoistAPI(self.__token)

        # get user current projects
        user_projects  = self.api.state['projects']
        with open('data/todoist-projects.csv', 'w') as file:
            file.write("Id" + "," + "Project" + "\n")
            for i in range(0, len(user_projects)):
                file.write('\"' + str(user_projects[i]['id']) + '\"' + "," + '\"' + str(user_projects[i]['name']) + '\"' + "\n")
        projects = pd.read_csv("data/todoist-projects.csv")

        # user completed stats info
        stats = self.api.completed.get_stats()
        # total completed tasks from stats
        user_completed_stats = stats['completed_count']
        self.get_completed_todoist_items(user_completed_stats)
        past_tasks = pd.read_csv("data/todost-raw-tasks-completed.csv")

        # get all current and previous projects
        # Extract all project ids used on tasks
        project_ids = past_tasks.project_id.unique()

        # Get Info on All User Projects
        project_names = []
        for i in project_ids:
            project_names.append(self.get_todoist_project_name(i))

        # Match Project Id Name on Completed Tasks, Add Day of Week
        # Probably a more effecient way to do this
        project_lookup = lambda x: self.get_todoist_project_name(x)
        past_tasks['project_name'] = past_tasks['project_id'].apply(project_lookup) # note: not very efficient

        # functions to convert UTC to Switzerland time zone and extract date/time elements
        convert_tz = lambda x: x.to_pydatetime().replace(tzinfo=np.pytz.utc).astimezone(np.pytz.timezone('Europe/Zurich'))
        get_year = lambda x: convert_tz(x).year
        get_month = lambda x: '{}-{:02}'.format(convert_tz(x).year, convert_tz(x).month) #inefficient
        get_date = lambda x: '{}-{:02}-{:02}'.format(convert_tz(x).year, convert_tz(x).month, convert_tz(x).day) #inefficient
        get_day = lambda x: convert_tz(x).day
        get_hour = lambda x: convert_tz(x).hour
        get_day_of_week = lambda x: convert_tz(x).weekday()

        # parse out date and time elements as Switzerland time
        past_tasks['completed_date'] = pd.to_datetime(past_tasks['completed_date'])
        past_tasks['year'] = past_tasks['completed_date'].map(get_year)
        past_tasks['month'] = past_tasks['completed_date'].map(get_month)
        past_tasks['date'] = past_tasks['completed_date'].map(get_date)
        past_tasks['day'] = past_tasks['completed_date'].map(get_day)
        past_tasks['hour'] = past_tasks['completed_date'].map(get_hour)
        past_tasks['dow'] = past_tasks['completed_date'].map(get_day_of_week)
        past_tasks = past_tasks.drop(labels=['completed_date'], axis=1)

        # save to CSV
        past_tasks.to_csv("data/todost-tasks-completed.csv", index=False)

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


