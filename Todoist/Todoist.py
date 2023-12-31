import tkinter as tk
from typing import List
import datetime
import pickle
import datetime
import os.path
import pandas as pd
import numpy as np
from todoist_api_python.api import Task
from todoist_api_python.api import TodoistAPI
import requests
import sys
import pytz
import matplotlib.pyplot as plt
import tkinter.ttk as ttk
from ttkwidgets import CheckboxTreeview

from Helpers.helpers import add_website_link, _from_rgb
from Credentials.Credentials import Credentials
from Configs.Parser import Parser

class Todoist():
    """
    Integrate the tasks from Todoist in the GUI
    """

    def __init__(self):
        """
        Initialize the Todoist class with the tasks from Todoist

        :param key: the key to access Todoist's API
        :type key: str
        :param window: the window frame where to place the tasks list
        :type window: ttk.Frame
        """
        self.__key = Credentials.get_todoist_credentials()
        if len(self.__key) == 0:
            print("Warning, Todoist credentials not found, will skip it")
        self.api = TodoistAPI(self.__key)

    def build_frame(self, window: ttk.Frame, bg_string: str, fg_string: str):
        """
        Build the frame for the TodoIst window

        :param window: the Frame of the Window
        :type window: ttk.Frame
        :param bg_string: the background color
        :type bg_string: str
        :param fg_string: the foreground color
        :type fg_string: str
        """
        self.window = window
        self.bg_string = bg_string
        self.fg_string = fg_string
        self.color_theme = Parser.get_plt_theme()
        self.color_palette = plt.get_cmap(self.color_theme)(np.linspace(0, 1, 7))[1:-1]
        self.tasks = self.get_tasks()

    def get_tasks(self) -> List[Task]:
        """
        Get the tasks that are in the section Work in Todoist and that are
        due in the next 2 days

        :return: the list of tasks to do
        :rtype: List[Task]
        """
        # maybe need to use this: api.get_project(project_id="2203306141") with only work project id
        today = datetime.datetime.now()
        after_tomorrow = f"{today.month}/{today.day+2}"
        try:
            tasks = self.api.get_tasks(
                filter = f"due before: {after_tomorrow} & #Work & /Work TODO")
        except Exception as e:
            print(e)
            tasks = []
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
        font = ('Aerial', '16', 'underline')
        side = "top"
        add_website_link(self.window, url, text, font, side,
                         fg = self.fg_string, bg = self.bg_string)

    def add_tasks_list(self):
        """
        Add the list of tasks to the right part of the main GUI
        """
        # projects -> list of length 4 wit each being a Project object
        # class attributes: dict_keys(['color', 'comment_count', 'id',
        # 'is_favorite', 'is_inbox_project', 'is_shared', 'is_team_inbox',
        # 'name', 'order', 'parent_id', 'url', 'view_style'])

        # Make a scrollbar for tasks that are overdue/due soon
        scrollbar = ttk.Scrollbar(self.window)
        self.tasks_listbox = CheckboxTreeview(self.window,
                                              yscrollcommand=scrollbar.set,
                                              show="tree",
                                              height=5)
        scrollbar.configure(command=self.tasks_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.tasks_listbox.pack(side="left", fill="both", expand=True)

        # we add colors from purple for overdue tasks to yellow for tasks due but
        # with lower importance
        colors = [_from_rgb(color) for color in self.color_palette]
        colors.reverse()
        self.task_colors = []
        # Get each task, color it depending on condition and add it to the listbox
        for i, task in enumerate(self.tasks):
            due_date = task.due.date.split("-")
            due_date = datetime.date(int(due_date[0]),
                                    int(due_date[1]),
                                    int(due_date[2]))
            if (due_date-datetime.date.today()).days<0:
                color = colors[4]
            else:
                color = colors[task.priority-1]
            self.task_colors.append(color)
            self.tasks_listbox.insert('', i,
                                    text=task.content+" due: "+str((due_date-datetime.date.today()).days+1),
                                    tags=(color,))
        self.tasks_listbox.bind('<<TreeviewSelect>>', self.update)
        for color in colors:
            self.tasks_listbox.tag_configure(color,
                                             background=color,
                                             font=('Aerial', 16),
                                             foreground = 'black')

    def update(self, event: tk.Event):
        """
        Remove task from TodoIst when the task is clicked

        :param event: the checkbox of the task is clicked
        :type event: tk.Event
        """
        tree = event.widget
        selection = tree.item(tree.selection())['tags'][1]
        if selection=="checked":
            task_done = [task for task in self.tasks if task.content.startswith(tree.item(tree.selection())['text'][:-10])][0]
            try:
                self.api.close_task(task_done.id)
            except Exception as error:
                print(error)

    def save_data(self, __backup_path):
        try:
            tasks_saved = pd.read_csv(os.path.join(__backup_path, 'todoist_tasks_completed.csv'))
            # tasks_saved.sort_values(['date', 'hour'], inplace=True)
            # tasks_saved.to_csv('data/todoist_tasks_completed.csv')
            tasks_last_save = [tasks_saved['date'].iloc[-1], tasks_saved['hour'].iloc[-1]]
        except FileNotFoundError:
            tasks_last_save = ['2023-10-10', 0]

        # # get user current projects
        # user_projects  = self.api.get_projects()
        # with open('data/todoist-projects.csv', 'w') as file:
        #     file.write("Id" + "," + "Project" + "\n")
        #     for i in range(0, len(user_projects)):
        #         file.write('\"' + str(user_projects[i].id) + '\"' + "," + '\"' + str(user_projects[i].name) + '\"' + "\n")
        # projects = pd.read_csv("data/todoist-projects.csv")

        headers = {'Authorization': f'Bearer {self.__key}'}
        # r = requests.get('https://api.todoist.com/sync/v9/completed/get_all', headers=headers).json()
        # stats = requests.get('https://api.todoist.com/sync/v9/completed/get_stats', headers=headers).json()
        # print(r.json())

        # user completed stats info
        stats = requests.get('https://api.todoist.com/sync/v9/completed/get_stats', headers=headers).json()
        # total completed tasks from stats
        user_completed_stats = stats['completed_count']
        past_tasks = self.get_completed_todoist_items(user_completed_stats, headers, tasks_last_save)
        # past_tasks = pd.read_csv("data/todost-raw-tasks-completed.csv")

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
        convert_tz = lambda x: x.to_pydatetime().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Zurich'))
        get_year = lambda x: convert_tz(x).year
        get_month = lambda x: '{}-{:02}'.format(convert_tz(x).year, convert_tz(x).month) #inefficient
        get_date = lambda x: '{}-{:02}-{:02}'.format(convert_tz(x).year, convert_tz(x).month, convert_tz(x).day) #inefficient
        get_day = lambda x: convert_tz(x).day
        get_hour = lambda x: convert_tz(x).hour
        get_day_of_week = lambda x: convert_tz(x).weekday()

        # parse out date and time elements as Switzerland time
        past_tasks['completed_at'] = pd.to_datetime(past_tasks['completed_at'])
        past_tasks['year'] = past_tasks['completed_at'].map(get_year)
        past_tasks['month'] = past_tasks['completed_at'].map(get_month)
        past_tasks['date'] = past_tasks['completed_at'].map(get_date)
        past_tasks['day'] = past_tasks['completed_at'].map(get_day)
        past_tasks['hour'] = past_tasks['completed_at'].map(get_hour)
        # dow is day of the week, 0 = Monday, 6 = Sunday
        past_tasks['dow'] = past_tasks['completed_at'].map(get_day_of_week)
        session_dict = {}
        for section in past_tasks['section_id'].unique():
            session_dict[section] = self.api.get_section(section_id="137257370").name
        past_tasks['section'] = [session_dict[sess] for sess in past_tasks['section_id']]
        past_tasks = past_tasks.drop(labels=['completed_at'], axis=1)
        # for i, row in past_tasks.iterrows():
        #     task = requests.get("https://api.todoist.com/sync/v9/items/get", headers=headers, data={'item_id': row['id']})

        # save to CSV
        past_tasks.to_csv(os.path.join(__backup_path, "todoist-tasks-completed.csv"), index=False)
        print("finished")

    def get_completed_todoist_items(self, user_completed_stats, headers, tasks_last_save):
        # create df from initial 50 completed tasks
        print("Collecting Initial 50 Completed Todoist Tasks...")
        # you can add completed since as parameter
        temp_tasks_dict = requests.get('https://api.todoist.com/sync/v9/completed/get_all', headers=headers).json()
        past_tasks = pd.DataFrame.from_dict(temp_tasks_dict['items'])
        # get the remaining items
        pager = list(range(50,user_completed_stats,50))
        for count, item in enumerate(pager):
            tmp_tasks = (self.api.completed.get_all(limit=50, offset=item))
            tmp_tasks_df = pd.DataFrame.from_dict(tmp_tasks['items'])
            past_tasks = pd.concat([past_tasks, tmp_tasks_df])
            print("Collecting Additional Todoist Tasks " + str(item) + " of " + str(user_completed_stats))
        # save to CSV
        print(len(past_tasks))
        past_tasks_copy = past_tasks.copy()
        for i, past_task in past_tasks.iterrows():
            if datetime.datetime.strptime(past_task['completed_at'], "%Y-%m-%dT%H:%M:%S.%fZ").date() < datetime.datetime.strptime(tasks_last_save[0], '%Y-%m-%d').date():
                past_tasks_copy.drop(i, inplace=True)
                # if datetime.datetime.strptime(past_task['completed_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        past_task = past_tasks_copy
        print(len(past_tasks))
        print("...Generating CSV Export")
        return past_tasks
        # past_tasks.to_csv("data/todost-raw-tasks-completed.csv", index=False)

     # get project info from Todoist API

    def get_todoist_project_name(self, project_id: str):
        item = self.api.get_project(project_id = project_id)
        if item:
            try:
                return item.name
            except:
                return item.project.name


