import ast
import os
from typing import List
import json
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime

def convert_to_datetime(df):
    # put in datetime for easier analysis
    df['ts'] = pd.to_datetime(df['ts'], format='%Y-%m-%dT%H:%M:%SZ')

def get_milliseconds_by_year(df):
    # get the number of milliseconds by year
    ms_played_by_year = df['ms_played'].groupby(df.ts.map(lambda t: t.year)).sum()
    # time is in ms -> put it in hours -> ms -> s -> h
    sns.barplot(x=ms_played_by_year.index, y=ms_played_by_year.values/MS_TO_H)
    plt.xlabel("Year")
    plt.ylabel("Time [h]")
    plt.show()

def through_the_day():
    # how do I listen to music throughout the day
    through_day = df.groupby(df.ts.map(lambda t: t.hour))['ms_played'].sum()
    sns.barplot(x=through_day.index, y=through_day.values/MS_TO_H)
    plt.xlabel("Hour")
    plt.ylabel("Time [h]")
    plt.show()

def get_category(df):
    # let's look at the different columns of the df
    df.username.unique() # gives jamesbardet
    df.platform.unique() # gives a lot of either phone / Windows (Idk why so many) -> maybe look for the number of phones I had
    df.conn_country.unique() # gives a list of countries -> could show on a map
    df.master_metadata_track_name.unique() # -> all the tracks
    df.master_metadata_album_artist_name.unique() # -> artist
    df.master_metadata_album_album_name.unique() # -> albums
    df.episode_name.unique() # podcasts' epsiodes
    df.episode_show_name.unique() # podcast's name e.g. Popcorn
    df.reason_start.unique() # []'clickrow' -> cliker dessus, 'fwdbtn' -> next chanson, 'trackdone' -> celle d'avant finit, 'appload'-> first song when load, 'backbtn' -> retour ?, '', 'trackerror', 'playbtn -> play', 'clickside', 'remote', 'unknown']
    df.reason_end.unique() # ['fwdbtn' -> next song, 'endplay' -> fermer appli ou juste stop, 'trackdone' -> finis entierement, 'unknown', 'clickrow' -> clicker sur une autre chanson, 'appload' -> problème de l'app, 'backbtn' -> retour, '', 'trackerror', 'logout', 'clickside', 'unexpected-exit-while-paused', 'unexpected-exit', 'remote']
    df.shuffle.unique() # false or true
    df.skipped.unique() # [True, False, None]
    df.offline.unique() # [False, True, None] -> can analyze for artists more offline or online maybe ? or songs?
    df.offline_timestamp.unique() # This field is a timestamp of when offline mode was used, if used.
    df.incognito_mode.unique() # [False,  True] -> only 68 rows, not interesting


