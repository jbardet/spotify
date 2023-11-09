# adapted from https://towardsdatascience.com/spotify-wrapped-data-visualization-and-machine-learning-on-your-top-songs-1d3f837a9b27
# https://github.com/areevesman/spotify-wrapped/blob/main/code/01_Data_Visualization.ipynb

import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from typing import List, Tuple
import pandas as pd
from matplotlib.patches import Polygon
from wordcloud import WordCloud
from typing import Dict
import tkinter.ttk as ttk
import json
import math
from .DraggablePoint import DraggablePoint
from .helpers import add_website_link, set_plot_color, _from_rgb, round_point_00_2
from .SpotifyPlayer import SpotifyPlayer
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from ..Database import Database
    from ..Client import APIClient
except ImportError:
    import sys
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))

    from Database import Database
    from Client import APIClient

# plt.switch_backend('agg')


class Radar():
    """
    Interactive Radar plot class to choose parameters to create playlists
    """
    def __init__(self, spotify_cr: Dict[str, str], db_cr: Dict[str, str],  window: ttk.Frame, bg_string:str, fg_string:str, color_theme: str):
        self.window = window
        self.move_flag = False
        self.area = None
        self.__db_id = db_cr['id']
        self.__db_password = db_cr['password']
        self.__db_name = db_cr["db_name"]
        self.__spotify_cr = spotify_cr
        self.bg_string = bg_string
        self.fg_string = fg_string
        self.color_theme = color_theme
        self.color_palette = plt.get_cmap(self.color_theme)(np.linspace(0, 1, 7))[1:-1]

        # add spotify website link on to spotify
        text = "Spotify"
        url = "https://open.spotify.com/?"
        font= ('Aerial', '16', 'underline')
        side = "top"
        add_website_link(self.window, url, text, font, side, fg = self.fg_string, bg = self.bg_string)

        # # Test of some genres analysis
        # self.analyze_artists()

        # features that we get from the database and that we're most interested in
        self.cols = ['acousticness', 'energy', 'danceability', 'valence',
                     'liveness', 'speechiness', 'instrumentalness', 'loudness',
                     'tempo']

        # the limits are taken based on the stats of the spotify features database,
        # maybe automate this with only min and max to search through the db
        self.limits = [[0,1], [0,1], [0,1], [0,1], [0,1], [0,1],
                       [0,1], [4,-60], [0,250]]
        acousticness = round_point_00_2(0.8960419161676647) # [0,1]
        energy = round_point_00_2(0.1208794011976048) # [0,1]
        danceability = round_point_00_2(0.44205808383233536) # [0,1]
        valence = round_point_00_2(0.12030898203592814) # [0,1]
        liveness = round_point_00_2(0.11084431137724553) # [0,1]
        speechiness = round_point_00_2(0.03765808383233533) # [0, 1]
        instrumentalness = round_point_00_2(0.8793353293413173) # [0, 1]
        loudness = round_point_00_2(1-0.6144068255094315) #[0,-60]
        tempo = round_point_00_2(0.3502247448161624) # [0, 250]

        # Generate the angles for all the features
        self.angles = np.linspace(0, 2 * np.pi, len(self.cols),
                                  endpoint=False).tolist()
        self.values = [acousticness, energy, danceability, valence, liveness,
                   speechiness, instrumentalness, loudness, tempo]
        self.angles += self.angles[:1]
        self.values += self.values[:1]
        # n = math.ceil(len(self.values)/3)
        # label_frames = []
        # for _ in range(n):
        #     label_frame =  ttk.Frame(self.window)
        #     label_frame.pack(side='top', anchor='c', fill='both', expand=True)
        #     label_frames.append(label_frame)
        label_frame = ttk.Frame(self.window)
        label_frame.pack(side='top', anchor='c', fill='both', expand=True)
        label_frame.grid_columnconfigure(tuple(range(3)), weight=1)
        label_frame.grid_rowconfigure(tuple(range(3)), weight=1)
        self.display_labels(label_frame)
        self.add_playlist_buttons()
        # Initialize the violin plots to show the distribution of the data
        self.violin_pos, self.violin_neg = None, None

        # let's make a spotify player to play songs
        spotify_player_frame = ttk.Frame(self.window)
        spotify_player_frame.pack(side='bottom', anchor='c', fill='both', expand=True)
        self.spotify_player = SpotifyPlayer(spotify_player_frame, self.__spotify_cr, self.fg_string, self.bg_string)

    def analyze_artists(self) -> None:
        """
        Test to analyze artists and their genres
        """
        # get the artists from the database
        db = Database(self.__db_id, self.__db_password, self.__db_name)
        artists = db.get_artists()
        columns = [column[0] for column in db.get_column_names_artists()]
        # create a dataframe with columns and values with artists
        df = pd.DataFrame(artists, columns = columns)
        # count genres and sort by count
        word_list = []
        for word in df['genres']:
            word = word.replace("}", "")
            word = word.replace("{", "")
            word = word.replace('"', "")
            # print(word)
            # words = word.split("[\\s,]")
            words = word.split(",")
            # print(words)
            # for word in words:
            #     word = word.split(" ")
            #     word_list.extend(word)
            word_list.extend(words)
        # make a single string from the list
        word_list = " ".join(word_list)
        wordcloud = WordCloud().generate(word_list)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
        print("OE")

    def add_playlist_buttons(self):
        """
        Add buttons to the GUI to display some playlists and update graph accordingly
        """
        # add a button for each playlist
        # Show examples of playlists' distributions
        playlist_frame = ttk.Frame(self.window)
        playlist_frame.pack(side='top', anchor='c', fill='both', expand=True)
        try:
            with open("Playlists/playlists.json", "r") as file:
                playlists = json.load(file)[0]
        except FileNotFoundError:
            with open(os.path.join(sys.path[-1], "Playlists/playlists.json"), "r") as file:
                playlists = json.load(file)[0]
        # for key, value in playlists.items():
        #     show_playlist
        # current_table = ttk.StringVar() # create variable for table
        # combo = ttk.Combobox(playlist_frame, values = list(playlists.keys()))
        # self.config
        # # (playlist_frame, text = key, command = lambda value=value: self.show_playlist(value))
        # button.pack(side = ttk.LEFT)
        text_font=('Aerial', 16)
        table = TableDropDown(playlist_frame, list(playlists.keys()), font=text_font)
        def print_value():
            print(table.current_table.get())
            self.show_playlist(playlists[table.current_table.get()])
        playlist_frame.option_add('*TCombobox*Listbox.font', text_font)
        table.pack(side="left", anchor = 'c',fill='both', expand=True)

        b = ttk.Button(playlist_frame, text='Show playlist', command = print_value,
                       style='my.TButton')
        b.pack(side = "left", anchor = 'c',fill='both', expand=True)
        # print(table.table.get())

    def show_playlist(self, values: dict):
        """
        Update graph based on playlist stats found in the db
        """
        db = Database(self.__db_id, self.__db_password, self.__db_name)
        playlist_names = list(values.keys())
        tracks_features = {
                'acousticness': [],
                'energy': [],
                'danceability': [],
                'valence': [],
                'liveness': [],
                'speechiness': [],
                'instrumentalness': [],
                'loudness': [],
                'tempo': []
            }
        columns = [column[0] for column in db.get_column_names()]
        for playlist_name in playlist_names:
            playlist_tracks = db.get_playlist_tracks(playlist_name)
            for track in playlist_tracks[1:-1].split(","):
                track_features = db.retrieve_feature(track)[0]
                for key in tracks_features.keys():
                    tracks_features[key].append(track_features[columns.index(key)])
                # tracks_features.append(track_features)
            # print(tracks_features)
        df = pd.DataFrame.from_dict(tracks_features)
        for i, col in enumerate(self.cols):
            violin_pos, violin_neg = self.get_violin(df[col], i)
            violin_pos.set_alpha(0.5)
            violin_neg.set_alpha(0.5)
            self.violins.append([violin_pos, violin_neg])

    def display_labels(self, window = ttk.Frame) -> None:
        """
        Display the labels of the variables on the GUI
        """
        self.labels = []
        for i in range(len(self.cols)):
            # create a label for each variable and place it on the GUI on the left
            # part of the window, each one down the other
            text = tk.StringVar()
            text.set(self.cols[i]+": "+ str(self.values[i]))
            # label = ttk.Label(window[i//3], text = text.get(), font=("Arial",14))
            label = ttk.Label(window, text = text.get(), font=("Arial",14))
            # increase size of label text
            # label.config(font=("Arial", 12), background='white')
            # TODO: change and place closer to the graph's axes
            # label.place(x = 20, y = 60 + 60 * i)
            # label.pack(side = tk.LEFT, anchor = 'c', fill='both', expand=True)
            label.grid(row=i//3, column=i%3, sticky="nsew")
            # label.place(anchor='center', relx =i//3*0.5, rely=i%3*0.3)
            self.labels.append(label)

    def change_value(self, i: int) -> None:
        """
        Change the value of the variable at index i on the GUI

        :param i: the variable that was changed by a drag and drop event
        :type i: int
        """
        self.values[i] = round_point_00_2(self.values[i])
        self.labels[i].configure(text = self.cols[i]+": "+str(self.values[i]))

    def update_plot_line(self) -> None:
        """
        Updates the plot fill lines based on the placement of points
        """
        for area in self.area:
            area.remove()
        self.area = self.ax.fill(self.angles, self.values, color=_from_rgb(self.color_palette[0]), alpha=0.7)

    def create_draggable_points(self, canvas: tk.Canvas) -> List[DraggablePoint]:
        """
        Creates a draggable point for each variable

        :param canvas: the Canvas where the figure is
        :type canvas: Canvas
        :return: _description_
        :rtype: List[DraggablePoint]
        """
        points = []
        for i in range(len(self.angles)):
            # add self to you can pass a reference to the Graph instance to
            # the Point class when you create the points
            point = DraggablePoint(self, canvas, self.ax, self.angles, self.values, i, _from_rgb(self.color_palette[-1]))
            points.append(point)
        return points

    def show_histogram(self, i: int):
        """
        Show the histogram of data values when moving the button around

        :param i: the index of the variable to show violin plot
        :type i: int
        """
        if i>=len(self.violins):
            i=0
        self.violins[i][0].set_alpha(0.5)
        self.violins[i][1].set_alpha(0.5)

    def remove_histogram(self, i: int):
        """
        Remove the histograms from the figure

        :param i: the index of the variable to remove violin plot
        :type i: int
        """
        self.violins[i][0].set_alpha(0)
        self.violins[i][1].set_alpha(0)
        # self.violin_pos.remove()
        # self.violin_neg.remove()
        # self.violin_pos.set_visible(False)
        # self.violin_pos.set_visible(False)
        # [p.remove() for p in reversed(self.ax.patches)]
        # self.ax.clear() # this removes all

    def plot_radar(self):
        """
        Plot the Radar graph on the GUI
        """

        fig, (self.ax) = plt.subplots(1, 1, figsize = (7, 7),
                                      subplot_kw=dict(polar=True))

        # Fix axis to go in the right order and start at 12 o'clock.
        self.ax.set_theta_offset(np.pi / 2)
        self.ax.set_theta_direction(-1)

        # Draw axis lines for each angle and label with its associated value.
        self.ax.set_thetagrids(np.degrees(self.angles[:-1]), self.cols, fontsize=14)

        # You can also set gridlines manually like this:
        self.ax.set_rgrids([0, 0.2, 0.4, 0.6, 0.8, 1], fontsize=12)

        # Create a colormap from green to red
        db = Database(self.__db_id, self.__db_password, self.__db_name)
        db_data = db.get_all()
        df = pd.DataFrame(db_data)
        df_columns = db.get_column_names()
        df_columns = [col[0] for col in df_columns]
        df.columns = df_columns

        self.violins = []
        for i, col in enumerate(self.cols):
            # normalize the column so that rounding is then equivalent everywhere
            violin_pos, violin_neg = self.get_violin(df[col], i)
            violin_pos.set_alpha(0)
            violin_neg.set_alpha(0)
            self.violins.append([violin_pos, violin_neg])

        self.ax.set_rlabel_position(40)
        plt.autoscale(enable=False)
        fig, self.ax = set_plot_color(fig, self.ax, self.fg_string)

        canvas = FigureCanvasTkAgg(fig, master = self.window)
        canvas_widget = canvas.get_tk_widget()
        canvas.get_tk_widget().config(bg=self.bg_string)
        canvas_widget.pack(side = tk.TOP)

        points = self.create_draggable_points(canvas)
        self.area = self.ax.fill(self.angles, self.values, color=_from_rgb(self.color_palette[0]), alpha=0.7)

        # add a button to create a playlist
        self.button = ttk.Button(self.window, text = "Create Playlist",
                                 command = self.create_playlist,
                                 style='my.TButton')
        self.button.pack(side = tk.BOTTOM)

        self.window.mainloop()

    def convert_to_polar(self, x: float, y: float) -> Tuple[float, float]:
        """
        Convert cartesian coordinates to polar coordinates

        :param x: the x position in cartesian coordinates
        :type x: float
        :param y: the y position in cartesian coordinates
        :type y: float
        :return: the angle and radius of the point in polar coordinates
        :rtype: Tuple[float, float]
        """
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        return np.pi/2-theta, r

    def get_violin(self, serie: pd.Series, i: int) -> Tuple[Polygon, Polygon]:
        """
        Get the violin plot from the data distribution

        :param serie: the datframe column of the feature we are interested in
        :type serie: pd.Series
        :param i: the feature index
        :type i: int
        :return: The positive and negative violin plots (to plot on the 2 sides
                    of the points)
        :rtype: Tuple[Polygon, Polygon]
        """
        col_normalized = (serie-self.limits[i][0])/(self.limits[i][1]-self.limits[i][0])
        polygon_data_points = col_normalized.round(1).value_counts().sort_index().reset_index().to_numpy()
        # normalize between 0 and 1 the second dimension of the array
        polygon_data_points[:,1] = polygon_data_points[:,1]/(10*polygon_data_points[:,1].max())
        # add data points to the polygon_data_points array
        polygon_data_points = np.flip(polygon_data_points, axis=1)

        # convert coordinates to polar coordinates
        polygon_polar_data_points = []
        for data_point in polygon_data_points:
            polygon_polar_data_points.append(self.convert_to_polar(data_point[0], data_point[1]))
        polygon_polar_data_points = np.insert(polygon_polar_data_points, 0, [[0,0]], axis=0)
        polygon_polar_data_points = np.append(polygon_polar_data_points, [[0,1]], axis=0)
        polygon_polar_data_points[:,0] = polygon_polar_data_points[:,0]+i*2*np.pi/len(self.cols)

        # creates the violinplot from the Polygons
        violin_pos = Polygon(np.array(polygon_polar_data_points), color = self.fg_string, alpha=0.5)
        self.ax.add_patch(violin_pos)
        # create the same polygon but now with negative values
        polygon_polar_data_points[:,0] = 4*i*np.pi/len(self.cols)-polygon_polar_data_points[:,0]
        violin_neg = Polygon(np.array(polygon_polar_data_points), color = self.fg_string, alpha=0.5)
        self.ax.add_patch(violin_neg)

        return violin_pos, violin_neg

    def create_playlist(self) -> None:
        """
        Creates a playlists based on the songs found in the database
        """
        client = APIClient([self.__spotify_cr['username']], [self.__spotify_cr['client_id']],
            [self.__spotify_cr['client_secret']])
        self.songs = self.search_for_songs()
        if len(self.songs)>0:
            client.create_playlist(self.songs, "Test Playlist")
        else:
            # display a message if no songs were found on the GUI
            label = ttk.Label(self.window, text = "No songs found, please modify parameters")
            label.pack()
            # maybe later give direction what to change to find things

    def search_for_songs(self):
        """
        Search in the database the songs that are associated with the values of
        the variables and display them on the GUI
        But we don't want more than 20 songs so that playlists are 1h long max
        but no more than 50 (you can only add 100 at a time)
        Research algorithm needs to be improved, maybe add genre diversity also.
        For now maybe only take random songs for the parameters
        """
        db = Database(self.__db_id, self.__db_password, self.__db_name)
        values, boundaries = self.rebalance()
        songs = db.get_songs(self.cols, values, boundaries)
        if len(songs)<20:
            factor = 2
            boundaries = self.modify_boundaries(boundaries, factor)
            songs = db.get_songs(self.cols, values, boundaries)
        # select 20 songs randomly
        songs = [song[0] for song in songs]
        songs = np.random.choice(songs, 20, replace=False)
        # songs = []
        # criteria = 20<=len(songs)<=50
        # while not criteria:
        #     songs = db.get_songs(self.cols, values, boundaries)
        #     print(len(songs))
        #     if len(songs)>=100:
        #         factor = 0.75
        #     elif len(songs)<20:
        #         factor = 2
        #     else: return songs
        #     boundaries = self.modify_boundaries(boundaries, factor)
        return songs

    def modify_boundaries(self, boundaries: List[float],
                          factor: int) -> List[float]:
        """
        Modify the boundaries of the variables to search for more songs in the
        database

        :param boundaries: _description_
        :type boundaries: List[float]
        :param factor: _description_
        :type factor: int
        :return: _description_
        :rtype: List[float]
        """
        boundaries = [boundary*factor for boundary in boundaries]
        return boundaries

    def rebalance(self) -> Tuple[List[float], List[float]]:
        """
        Rebalance the values of the variables so that they are in the range of
        the limits

        :return: the new values of the variables
        :rtype: Tuple[List[float], List[float]]
        """
        values = []
        boundaries = []
        for i in range(len(self.values)-1):
            boundaries.append(np.abs((self.limits[i][1]-self.limits[i][0])/10))
            if self.values[i] < self.limits[i][0]:
                values.append(self.limits[i][0])
            elif self.values[i] > self.limits[i][1]:
                values.append(self.limits[i][1])
            else:
                values.append(self.values[i]*(self.limits[i][1]-self.limits[i][0]))
        return values, boundaries

class TableDropDown(ttk.Combobox):
    def __init__(self, parent, values, font):
        self.current_table = tk.StringVar() # create variable for table
        ttk.Combobox.__init__(self, parent, font=font)#  init widget
        self.config(textvariable = self.current_table, state = "readonly", values = values)
        self.current(0) # index of values for current table
        self.pack(side="left") # place drop down box
        # print(self.current_table.get())
