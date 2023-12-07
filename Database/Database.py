import paramiko
from sqlalchemy import create_engine
import psycopg2 as ps
from sshtunnel import SSHTunnelForwarder
import pandas as pd
from Configs.Parser import Parser
from typing import List

class Database:
    def __init__(self, __db_id, __db_password):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__db_id = __db_id
        self.__db_password = __db_password
        self.__db_name = Parser.get_db_name()
        self.__db_port = Parser.get_db_port()
        self.replacement = {
            "playlist": lambda x: x[:3]+x[4:],
            "artist": lambda x: [x[0]]+[x[1] + " | " + x[2]]+x[3:],
            "feature": lambda x: [x[0] + " | " + x[1]]+x[2:],
            "playlist_feature": lambda x: print("not solved")
        }
        try:
            self.initialize()
            self.shutdown()
        except TimeoutError:
            print("Unable to reach the Database, will not show features but will save data to Drive")
            raise

    def initialize(self):
        retry=True
        i=0
        while retry:
            try:
                self.ssh.connect(self.__db_port, username=self.__db_id, password=self.__db_password)
                retry = False
                print("connected")
            except TimeoutError as e:
                # TimeoutError: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond
                # Raspberry pi is not on
                print(e)
                i+=1
                if i == 1:
                    raise
        command = f"psql {self.__db_name}"
        self.ssh_stdin, self.ssh_stdout, self.ssh_stderr = self.ssh.exec_command(command)

    def execute_command(self, command):
        print("execute")
        self.initialize()
        self.ssh_stdin.write(command)
        self.ssh_stdin.close()
        # print(self.ssh_stdin.read().decode('ascii'))
        if len(self.ssh_stderr.read().decode('ascii'))>0:
            print("Saving data failed")
        return self.ssh_stdout

    def parse_results(self, results, replacement):
        res = results.readlines()
        values = []
        for i, line in enumerate(res):
            # res[0] is columns
            # res[1] is only ----
            if i==0:
                columns = [l.strip() for l in line.split("|")]
            elif i == 1:
                continue
            elif i==len(res)-1 or i==len(res)-2:
                continue
            else:
                vals = [l.strip() for l in line.split("|")]
                if len(vals)>len(columns):
                    too_long = len(vals)-len(columns)
                    for i in range(too_long):
                        vals = replacement(vals)
                values.append(vals)
        # df = pd.DataFrame(values, columns=columns_)
        self.shutdown()
        print("finished")
        return columns, values

    def parse_command(self, command, replacement=None):
        return self.parse_results(self.execute_command(command), replacement)

    def shutdown(self):
        self.ssh.close()

    def get_playlists_tracks(self, names: List[str]):
        if len(names)==1:
            command = f"SELECT tracks FROM playlists WHERE name = '{names[0]}';"
        else:
            command = (f"SELECT tracks FROM playlists WHERE name IN {tuple(names)};")
        try:
            _, values = self.parse_command(command, self.replacement['playlist'])
        except UnboundLocalError:
            print(f"{names} failed")
            _, values = self.parse_command(command, self.replacement['playlist'])
        res = []
        for val in values:
            res.extend(val[0][1:-1].split(","))
        return set(res)

    def get_playlist_tracks(self, name):
        command = (f"SELECT tracks FROM playlists WHERE name='{name}';")
        _, values = self.parse_command(command, self.replacement['playlist'])
        return values[0][0][1:-1].split(",")

    def get_playlist_id(self, name):
        command = (f"SELECT id FROM playlists WHERE name='{name}';")
        _, values = self.parse_command(command, self.replacement['playlist'])
        return values[0][0]

    def get_playlist_names(self):
        command = ("SELECT * FROM playlists;")
        columns, values = self.parse_command(command, self.replacement['playlist'])
        return columns, values

    def save_artists_to_db(self, df: pd.DataFrame):
        pass

    def is_artist_in_db(self, id: str):
        command = (f"SELECT EXISTS(SELECT 1 FROM artists WHERE id='{id}');")
        return command

    def get_artists(self):
        command = ("SELECT * FROM artists;")
        columns, values = self.parse_command(command, self.replacement['artists'])
        return columns, values

    def is_track_in_db(self, id: str):
        command = (f"SELECT EXISTS(SELECT 1 FROM features WHERE id='{id}');")
        return command

    def get_songs(self, cols, values, boundaries):
        command = (f"SELECT id FROM features WHERE ")
        i=0
        for col, val, boundary in zip(cols, values, boundaries):
            i+=1
            if i==8:
                continue
            command += f"{round(val-boundary, 1)}<={col} AND {col}<={round(val+boundary, 1)} AND "
        command = command[:-5] + ";"
        return self.parse_command(command, self.replacement['feature'])

    def save_feature(self, values):
        command = (f"INSERT INTO features VALUES ({values});")
        self.execute_command(command)
        return

    def get_all_features(self):
        command = ("SELECT * FROM features")
        return self.parse_command(command, self.replacement['feature'])

    def retrieve_features(self, ids: List[str]):
        command = (f"SELECT * FROM features WHERE id IN {tuple(ids)};")
        return self.parse_command(command, self.replacement['feature'])

    def retrieve_feature(self, id: str):
        command = (f"SELECT * FROM features WHERE id='{id}';")
        return self.parse_command(command, self.replacement['feature'])

    def save_history_data(self, data):
        data_to_insert = self.prepare_data_to_save(data)
        if data_to_insert:
            command = (f"INSERT INTO history VALUES " + data_to_insert)
            self.execute_command(command)
            self.shutdown()

    def save_liked_data(self, data):
        data_to_insert = self.prepare_data_to_save(data)
        if data_to_insert:
            command = (f"INSERT INTO liked VALUES " + data_to_insert)
            self.execute_command(command)
            self.shutdown()

    def get_timer_data(self):
        command = ("SELECT * FROM timer WHERE date_trunc('day', time) = date_trunc('day', current_timestamp);")
        return self.parse_command(command)

    def get_offline_data(self):
        command = ("SELECT * FROM offline WHERE date_trunc('day', date) = date_trunc('day', current_timestamp);")
        return self.parse_command(command)

    def prepare_data_to_save(self, data, suppress=0):
        number_data = len(data[list(data.keys())[0]])
        if number_data-suppress <= 0:
            return
        data_to_insert = ""
        for i in range(number_data-suppress):
            str_to_add = "("
            for key in data.keys():
                str_to_add+=f"'{data[key][i+suppress]}',"
            str_to_add = str_to_add[:-1] + ")"
            data_to_insert += str_to_add + ","
        data_to_insert = data_to_insert[:-1]+";"
        return data_to_insert

    def save_timer_data(self, timer_data, timer_suppress):
        data_to_insert = self.prepare_data_to_save(timer_data, timer_suppress)
        if data_to_insert:
            command = (f"INSERT INTO timer VALUES " + data_to_insert)
            self.execute_command(command)
            self.shutdown()

    def save_offline_data(self, offline_data, offline_suppress):
        data_to_insert = self.prepare_data_to_save(offline_data, offline_suppress)
        if data_to_insert:
            command = (f"INSERT INTO offline VALUES " + data_to_insert)
            self.execute_command(command)
            self.shutdown()

# if __name__ == "__main__":
#     # db = PlaylistDatabase()
#     # res = db.get_playlist_id('Perfect Concentration')
#     # print(res['tracks'])
#     # db = ArtistDatabase()
#     # db.is_artist_in_db("1")
#     # TODO: save_artists_to_db, save_playlists_to_db, save_feature_to_db


