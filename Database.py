import psycopg2 as ps
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
import pandas as pd
from sqlalchemy import create_engine

class Database:
    def __init__(self, username, password, data_base):
        self.host_name = 'localhost'
        self.data_base = data_base
        self.username = username
        self.password = password
        self.port_id = '5432'

    def __create_engine(self):
        connection_string = f'postgresql://{self.username}:{self.password}@{self.host_name}:{self.port_id}/{self.data_base}'
        engine = create_engine(connection_string)
        return engine

    def get_playlist_tracks(self, name):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        command = ("SELECT tracks FROM playlists WHERE name = %s;")
        variables = (name,)
        curr.execute(command, variables)
        return curr.fetchall()[0][0]

    def save_artists_to_db(self, df: pd.DataFrame):
        conn = self.__connect_to_db()
        #creating the cursor to execute the SQL commands
        # curr = conn.cursor()
        engine = self.__create_engine()
        df.to_sql('artists', con=engine, if_exists='append',
          index=False)
        print("done")

    def save_playlists_to_db(self, df: pd.DataFrame):
        conn = self.__connect_to_db()
        #creating the cursor to execute the SQL commands
        # curr = conn.cursor()
        engine = self.__create_engine()
        df.to_sql('playlists', con=engine, if_exists='append',
          index=False)
        print("done")

    def save_feature_to_db(self, data: pd.DataFrame):
        # Store the data in the Local SQL Server database
        conn = self.__connect_to_db()
        #creating the cursor to execute the SQL commands
        curr = conn.cursor()
        # Loading the data to the database table
        # register_adapter(np.float64, addapt_numpy_float64)
        # register_adapter(np.int64, addapt_numpy_int64)
        self.__update_database(curr, conn, data)
        # command = "ALTER TABLE features ADD PRIMARY KEY (id);"
        # curr.execute(command)

    #creating the connection function
    def __connect_to_db(self):
        try:
            conn = ps.connect(host = self.host_name, database = self.data_base,
                            user = self.username, password = self.password,
                            port = self.port_id)
        except ps.OperationalError as e:
            raise e
        # else:
            # print('Connected sucessfully!')

        return conn

    def _create_table(self, curr, command):
        curr.execute(command)

    def __check_video_exists(self, curr, video_id):
        query_select = ('''SELECT video_id FROM youtube_videos_freecodecamp WHERE video_id = %s;''')
        #To generate a one-element tuple, a comma , is required at the end.
        variable = (video_id,) #the variable that come from the df and goes to the sql query
        curr.execute(query_select, variable)
        record = curr.fetchone() #returns a single record or None if there is no row available.

        if record is not None: #it executes only if there is record (the video already exists)
            return record
        else:
            return False

    # Creating the function to go row by row in order to insert the new records
    def __append_from_df_to_db(self, curr, df):
        for i, row in df.iterrows():
            self.insert_new_videos(curr, row['video_id'], row['view_count'])

    #Defing the function to insert new records to the table database
    def __insert_new_videos(self, curr, video_id, view_count):
        query_insert_new_videos = ('''INSERT INTO youtube_videos_freecodecamp
                                    (video_id, view_count)
                                    VALUES (%s, %s);''')

        variables_insert = (video_id, view_count)
        curr.execute(query_insert_new_videos, variables_insert)

    #Defining the function which will update the database inserting new records and/or updating the metrics
    def __update_database(self, curr, conn, df):
        # Create a new empty df exactly before, which we will append the rows which never were stored in the database (for the first time, all records will be stored here since there are any records)
        # new_videos_df = pd.DataFrame(columns=["video_id", "view_count"])

        # for i, row in df.iterrows():
        #     if self.__check_video_exists(curr, row['name']): #if it is true, it will run the update_row function to refresh the view, like and comment counts
        #         # self.__update_row(curr, row['video_id'], row['view_count'])
        #         pass
        #     else: #if the video does not exist, it will append to the db table
        #         # new_videos_df = pd.concat([new_videos_df, pd.DataFrame([row])], ignore_index=True)
        self.__insert_data(curr, conn, df)
        # return new_videos_df

    def is_track_in_db(self, id: str):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        command = ("SELECT EXISTS(SELECT 1 FROM features WHERE id = %s);")
        variables = (id,)
        curr.execute(command, variables)
        return curr.fetchall()[0][0]

    def __insert_data(self, curr, conn, df):
        # conn.autocommit = True
        engine = self.__create_engine()
        df.to_sql('features', con=engine, if_exists='append',
          index=False)
        print("done")

        # #the variables that come from the df and go to the sql query
        # variables = (view_count)
        # curr.execute(query_update, variables)

    def __update_row(self, curr, video_id, view_count):
        query_update = ('''UPDATE youtube_videos_freecodecamp
                        SET view_count = %s;''')

        #the variables that come from the df and go to the sql query
        variables = (view_count)
        curr.execute(query_update, variables)

    def _get_query(self, query):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        # variable = (video_id,) #the variable that come from the df and goes to the sql query
        curr.execute(query) #, variable)
        record = curr.fetchall() #returns all rows corresponding to query
        # if needs one -> fetchone()
        # if record is not None: #it executes only if there is record (the video already exists)
        #     return record
        # else:
        #     return False
        return record

    def get_artists(self):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        # query = ('''SELECT * FROM features;''')
        query = ('''SELECT * FROM artists''')
        curr.execute(query)
        return curr.fetchall()

    def get_songs(self, cols, values, boundaries):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        # query = ('''SELECT * FROM features;''')
        query = ('''SELECT id FROM features WHERE ''')
        # variables = ()
        i=0
        for col, val, boundary in zip(cols, values, boundaries):
            i+=1
            if i==8:
                continue
            query += f"{round(val-boundary, 1)} <= {col} AND {col} <= {round(val+boundary, 1)} AND "
        query = query[:-5] + ";"
        curr.execute(query)
        return curr.fetchall()

    def get_all(self):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        query = ('''SELECT * FROM features''')
        curr.execute(query)
        return curr.fetchall()

    def retrieve_feature(self, id):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        command = ('''SELECT * FROM features WHERE id=%s;''')
        variables = (id,)
        curr.execute(command, variables)
        return curr.fetchall()

    def get_column_names_artists(self):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        query = ('''SELECT column_name FROM information_schema.columns WHERE table_name = 'artists' ORDER BY ordinal_position;''')
        curr.execute(query)
        return curr.fetchall()

    def get_column_names(self):
        conn = self.__connect_to_db()
        curr = conn.cursor()
        query = ('''SELECT column_name FROM information_schema.columns WHERE table_name = 'features' ORDER BY ordinal_position;''')
        curr.execute(query)
        return curr.fetchall()

    def get_features_from_playlists(self, playlist_name):
        column_names = [col[0] for col in self.get_column_names()]
        playlist_dic = {}
        for column_name in column_names:
            playlist_dic[column_name] = []
            playlist_id = playlist_name.split("/")[-1].split("?")[0]
            for playlist_api in playlists_api:
                if playlist_id == playlist_api["id"]:
                    for track in playlist_api['tracks']:
                        song_id = track['track']['id']
                        try:
                            song_features = features_db.retrieve_feature(song_id)[0]
                        except:
                            continue
                        for i, song_feature in enumerate(song_features):
                            playlist_dic[column_names[i]].append(song_feature)
                        # print(playlist_dic)
        playlist_dic

    # def add_features_to_db(self, features):

class FeatureDB(Database):
    def __init__(self, username, password):
        super().__init__(username, password, "spotify_artists")

    def create_table(self, curr):
        create_table_command = (''' CREATE TABLE IF NOT EXISTS youtube_videos_freecodecamp (
                                    video_id VARCHAR (300) PRIMARY KEY,
                                    view_count INT NOT NULL
                                );''')
        super()._create_table(create_table_command)

    def get_query(self):
        query = ('''SELECT * FROM features;''')
        super()._get_query(query)

class ArtistsDB(Database):
    def __init__(self, username, password):
        super().__init__(username, password,"features")

    def __create_table(self):
        create_table_command = (''' CREATE TABLE IF NOT EXISTS youtube_videos_freecodecamp (
                                    video_id VARCHAR (300) PRIMARY KEY,
                                    view_count INT NOT NULL
                                );''')
        super()._create_table(create_table_command)

    def get_query(self):
        query = ('''SELECT * FROM features;''')
        super()._get_query(query)

def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
