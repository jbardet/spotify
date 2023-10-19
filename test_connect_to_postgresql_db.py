import psycopg2 as ps
import pandas as pd
import numpy as np
from psycopg2.extensions import register_adapter, AsIs

def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)

def store_data_in_db(data):
    # Store the data in the Local SQL Server database
    host_name = 'localhost'
    data_base = 'features'
    user_name = 'james'
    password = 'Kkatecalisti98'
    port_id = '5432'

    conn = connect_to_db(host_name, data_base, user_name, password, port_id)

    #creating the cursor to execute the SQL commands
    curr = conn.cursor()
    create_table(curr)
    conn.commit()

    # Loading the data to the database table
    register_adapter(np.float64, addapt_numpy_float64)
    register_adapter(np.int64, addapt_numpy_int64)
    new_videos_df = update_database(curr, data)

def check_video_exists(curr, video_id):
    query_select = ('''SELECT video_id FROM youtube_videos_freecodecamp WHERE video_id = %s;''')
    #To generate a one-element tuple, a comma , is required at the end.
    variable = (video_id,) #the variable that come from the df and goes to the sql query
    curr.execute(query_select, variable)
    record = curr.fetchone() #returns a single record or None if there is no row available.

    if record is not None: #it executes only if there is record (the video already exists)
        return record
    else:
        return False

#Creating the function to go row by row in order to insert the new records
def append_from_df_to_db(curr, df):
    for i, row in df.iterrows():
        insert_new_videos(curr, row['video_id'], row['view_count'])

#Defing the function to insert new records to the table database
def insert_new_videos(curr, video_id, view_count):
    query_insert_new_videos = ('''INSERT INTO youtube_videos_freecodecamp
                                (video_id, view_count)
                                VALUES (%s, %s);''')

    variables_insert = (video_id, view_count)
    curr.execute(query_insert_new_videos, variables_insert)

#Defining the function which will update the database inserting new records and/or updating the metrics
def update_database(curr, df):
    # Create a new empty df exactly before, which we will append the rows which never were stored in the database (for the first time, all records will be stored here since there are any records)
    new_videos_df = pd.DataFrame(columns=["video_id", "view_count"])

    for i, row in df.iterrows():
        if check_video_exists(curr, row['video_id']): #if it is true, it will run the update_row function to refresh the view, like and comment counts
            update_row(curr, row['video_id'], row['view_count'])
        else: #if the video does not exist, it will append to the db table
            new_videos_df = pd.concat([new_videos_df, pd.DataFrame([row])], ignore_index=True)
    return new_videos_df

def update_row(curr, video_id, view_count):
    query_update = ('''UPDATE youtube_videos_freecodecamp
                    SET view_count = %s;''')

    #the variables that come from the df and go to the sql query
    variables = (view_count)
    curr.execute(query_update, variables)

def create_table(curr):
    create_table_command = (''' CREATE TABLE IF NOT EXISTS youtube_videos_freecodecamp (
                                video_id VARCHAR (300) PRIMARY KEY,
                                view_count INT NOT NULL
                            );''')
    curr.execute(create_table_command)

#creating the connection function
def connect_to_db(host_name, data_base, user_name, password, port_id):
    try:
        conn = ps.connect(host = host_name, database = data_base,
                          user = user_name, password = password,
                          port = port_id)
    except ps.OperationalError as e:
        raise e
    else:
        print('Connected sucessfully!')

    return conn

def main():
    df = pd.DataFrame(columns=["video_id", 'view_count'])
    df['video_id']= ["1","3","4","5"]
    df['view_count']= ["6","7","8","9"]
    store_data_in_db(df)

if __name__ == "__main__":
    main()