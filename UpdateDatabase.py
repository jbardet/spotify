import os
import json
from typing import List, Tuple
import spotipy
import argparse
import pandas as pd
from tqdm import tqdm

from Client import APIClient
from Database import Database

# When you have downloaded new history from spotify you will want to update your
# database based on this

class UpdateDatabase:
    def __init__(self, args: dict):
        self.username = ['jamesbardet'] # eval(args.username)
        self.id = ['4cbacd4796fe4ccd819bbf6315d5ea79'] # eval(args.id)
        self.secret = ['662bcdc685324cddad9a77435955e515'] # eval(args.secret)
        self.client = APIClient(self.username, self.id, self.secret)
        self.spotify_database = Database(username = 'james', #args.database,
                                         password = 'Kkatecalisti98', #args.password,
                                         data_base = "spotifydb")
        self.__BASEPATH = os.path.dirname(os.path.realpath(__file__))
        self.__DATAPATH = os.path.join(self.__BASEPATH, "MyData")
        self.__FEATURESPATH = os.path.join(self.__BASEPATH, "Features")
        self.__PLAYLISTSPATH = os.path.join(self.__BASEPATH, "Playlists")
        self.__ARTISTSPATH = os.path.join(self.__BASEPATH, "Artists")

        self.main()

    def main(self):

        # # directory where the feature information accessed through API will lie
        # if not os.path.isdir(self.__FEATURESPATH):
        #     os.mkdir(self.__FEATURESPATH)
        #     ids_done = []
        # else:
        #     ids_done = self.__get_uri_from_streams_done(self.__FEATURESPATH)

        # streamings = self.__get_streamings()
        # try:
        #     features = self.get_features_all_tracks(streamings, ids_done, self.client)
        # except Exception as e:
        #     print(e)
        #     raise
        # # save_feature_data(FEATURESPATH, features)
        # with open(os.path.join(self.__FEATURESPATH, "features.json"), 'r', encoding='UTF-8') as f:
        #     features = json.load(f)
        # features_db = pd.DataFrame(features)
        # features_db.drop_duplicates(subset='id', inplace=True)
        # self.spotify_database.save_feature_to_db(features_db)
        # print("Saved")
        # table = self.spotify_database.get_query()
        # print(table)

        # self.test_kaggle()

        # # Get playlists songs WARNING, NEED TO CHECK DUPLICATE
        # self.__get_playlists_songs()
        # print("done")
        features = self.__check_if_song_is_in_db()
        with open(os.path.join(self.__FEATURESPATH, "playlist_features_08_11.json"), 'w', encoding='UTF-8') as outfile:
            json.dump(features, outfile)
        with open(os.path.join(self.__FEATURESPATH, "playlist_features_08_11.json"), 'r', encoding='UTF-8') as f:
            features = json.load(f)
        features_db = pd.DataFrame(features)
        features_db.drop_duplicates(subset='id', inplace=True)
        self.spotify_database.save_feature_to_db(features_db)

        # streamings = self.__get_streamings()
        # if not os.path.isdir(self.__ARTISTSPATH):
        #     os.mkdir(self.__ARTISTSPATH)
        #     artists_done = []
        # else:
        #     artists_done = self.__get_uri_from_artists_done(self.__ARTISTSPATH)
        # artists = self.get_artists(streamings)
        # artists_infos, artists_and_related = self.ask_api_for_artists(artists, artists_done, self.client)
        # print(artists_infos, artists_and_related)
        # self.save_feature_data(self.__ARTISTSPATH, artists_and_related, "artists_and_related")
        # self.save_feature_data(self.__ARTISTSPATH, artists_infos, "artists_infos")
        # self.add_artists()
        # # # Artists
        # # # Load artists json file and add it to the artist table in the database
        # # with open(os.path.join(self.__ARTISTSPATH, "features.json"), 'r', encoding='UTF-8') as f:
        # #     artists = json.load(f)
        # # print(artists)
        # # for artist in artists:
        # #     artist_name = list(artist.keys())[0]
        # #     # then list of 20 properties as values -> related artists
        # #     # that are dict: ['external_urls', 'followers', 'genres', 'href', 'id', 'images', 'name', 'popularity', 'type', 'uri']
        # #     # save each as id, name, followers['total'], popularity, genres, related_artists (but only for the first)

        # # Playlists
        # # # Load playlists json file and add it to the playlist table in the database
        # with open(os.path.join(self.__PLAYLISTSPATH, "playlists.json"), 'r', encoding='UTF-8') as f:
        #     playlists = json.load(f)
        # for first_key, values in playlists.items():
        #     for second_key, value in values.items():
        #         # database with second_key, value, first_key
        #         # which would be Deep Focus, https.., Deep Concentration
        #         pass

        # self.update_playlist_db()
        # # Load playlists json file and add it to the playlist table in the database
        # with open(os.path.join(self.__PLAYLISTSPATH, "playlists_api.json"), 'r', encoding='UTF-8') as f:
        #     playlists = json.load(f)
        # for playlist in playlists:
        #     # keys are ['collaborative', 'description', 'external_urls', 'followers', 'href', 'id', 'images', 'name', 'owner', 'primary_color', 'public', 'snapshot_id', 'type', 'uri', 'tracks']
        #     # tracks are ['added_at', 'added_by', 'is_local', 'primary_color', 'track', 'video_thumbnail']
        #     # track as ['album', 'artists', 'available_markets', 'disc_number', 'duration_ms', 'episode', 'explicit', 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'name', 'popularity', 'preview_url', 'track', 'track_number', 'type', 'uri']
        #     # maybe add in db: id, name, description, followers['total'], images[0]['url'], tracks
        #     # where tracks is a list of [track_id, track_name, track_popularity, artists_id, artists_name, duration_ms, explicit]
        pass

    # # spotify does not allow to have more recent history than 50 songs so won't use it here (would need to download data from link again)
    #     self.recent_history()
    # def recent_history(self):
    #     # ask spotify's api for the recent history of the user
    #     results1 = self.client.get_recently_played()
    #     # print(results1)
    #     results2 = self.client.get_recently_played_link(results1['next'])
    #     print(results2)

    def test_kaggle(self):
        import pandas as pd
        import json
        # load csv file with pandas
        # tracks = pd.read_csv("./kaggle/tracks.csv")
        artists = pd.read_csv("./kaggle/artists.csv")

        artists_dict = {
                'id': [],
                'name': [],
                'popularity': [],
                'followers': [],
                'images': [],
                'genres': []
            }
        # iterate through each row of the dataframe
        for index, row in artists.iterrows():
            # artist_name = list(artist.keys())[0]
            # for related_artist in artist[artist_name]:
            is_in_db = self.spotify_database.is_artist_in_db(row['id'])
            if not is_in_db:
                artists_dict['id'].append(row['id'])
                artists_dict['name'].append(row['name'])
                artists_dict['popularity'].append(row['popularity'])
                artists_dict['followers'].append(row['followers'])
                # urls = [image['url'] for image in related_artist['images']]
                artists_dict['images'].append(None)
                artists_dict['genres'].append(row['genres'])
            # else:
            #     print("Artist already in")

        # create dataframe from dict
        artists_df = pd.DataFrame.from_dict(artists_dict)
        self.spotify_database.save_artists_to_db(artists_df)
        # # These are recommanded artists from the artists (not useful)
        # with open("./kaggle/dict_artists.json", 'r', encoding='UTF-8') as f:
        #     dic = json.load(f)
        # # json_ = pd.DataFrame.from_dict(dic)
        # print(dic)
        print(artists)

        # tracks_dict = {
        #     'name': [],
        #     'danceability': [],
        #     'energy': [],
        #     'key': [],
        #     'loudness': [],
        #     'mode': [],
        #     'speechiness': [],
        #     'acousticness': [],
        #     'instrumentalness': [],
        #     'liveness': [],
        #     'valence': [],
        #     'tempo': [],
        #     'type': [],
        #     'id': [],
        #     'uri': [],
        #     'track_href': [],
        #     'analysis_url': [],
        #     'duration_ms': [],
        #     'time_signature': [],
        # }
        # # iterate through each row of the dataframe
        # for index, row in tracks.iterrows():
        #     is_track_in_db = self.spotify_database.is_track_in_db(row['id'])
        #     if not is_track_in_db:
        #         tracks_dict['name'].append(row['name'])
        #         tracks_dict['danceability'].append(row['danceability'])
        #         tracks_dict['energy'].append(row['energy'])
        #         tracks_dict['key'].append(row['key'])
        #         tracks_dict['loudness'].append(row['loudness'])
        #         tracks_dict['mode'].append(row['mode'])
        #         tracks_dict['speechiness'].append(row['speechiness'])
        #         tracks_dict['acousticness'].append(row['acousticness'])
        #         tracks_dict['instrumentalness'].append(row['instrumentalness'])
        #         tracks_dict['liveness'].append(row['liveness'])
        #         tracks_dict['valence'].append(row['valence'])
        #         tracks_dict['tempo'].append(row['tempo'])
        #         tracks_dict['type'].append(None)
        #         tracks_dict['id'].append(row['id'])
        #         tracks_dict['uri'].append(None)
        #         tracks_dict['track_href'].append(None)
        #         tracks_dict['analysis_url'].append(None)
        #         tracks_dict['duration_ms'].append(row['duration_ms'])
        #         tracks_dict['time_signature'].append(row['time_signature'])
        #     else:
        #         print("Track already in")
        # # create dataframe from dict
        # track_df = pd.DataFrame.from_dict(tracks_dict)
        # self.spotify_database.save_feature_to_db(track_df)
        print("oe")


    def add_artists(self):
        # Load artists json file and add it to the artist table in the database
        with open(os.path.join(self.__ARTISTSPATH, "features.json"), 'r', encoding='UTF-8') as f:
            artists = json.load(f)
        # print(artists)
        df_dict = {
                'id': [],
                'name': [],
                'popularity': [],
                'followers': [],
                'images': [],
                'genres': []
            }
        for artist in artists:
            artist_name = list(artist.keys())[0]
            for related_artist in artist[artist_name]:
                df_dict['id'].append(related_artist['id'])
                df_dict['name'].append(related_artist['name'])
                df_dict['popularity'].append(related_artist['popularity'])
                df_dict['followers'].append(related_artist['followers']['total'])
                urls = [image['url'] for image in related_artist['images']]
                df_dict['images'].append(urls)
                df_dict['genres'].append(related_artist['genres'])

        # create dataframe from dict
        artists_df = pd.DataFrame.from_dict(df_dict)
        self.spotify_database.save_artists_to_db(artists_df)

    def update_playlist_db(self):
        # Load playlists json file and add it to the playlist table in the database
        with open(os.path.join(self.__PLAYLISTSPATH, "playlists_api.json"), 'r', encoding='UTF-8') as f:
            playlists = json.load(f)
        df_dict = {
                'id': [],
                'name': [],
                'description': [],
                'followers': [],
                'images': [],
                'tracks': []
            }
        for playlist in playlists:
            tracks = []
            for playlist_track in playlist['tracks']:
            #     track = playlist_track['track']
            #     artist_ids = [artist['id'] for artist in track['artists']]
            #     artist_names = [artist['name'] for artist in track['artists']]
            #     # artist_ids = track['artists'][0]['id']
            #     # artist_names = track['artists'][0]['name']
            #     tracks.append([track['id'], track['name'], track['popularity'],
            #                    artist_ids, artist_names, track['duration_ms'], track['explicit']])
                tracks.append(playlist_track['track']['id'])
            df_dict['id'].append(playlist['id'])
            df_dict['name'].append(playlist['name'])
            df_dict['description'].append(playlist['description'])
            df_dict['followers'].append(playlist['followers']['total'])
            df_dict['images'].append(playlist['images'][0]['url'])
            df_dict['tracks'].append(tracks)

        # create dataframe from dict
        playlists_df = pd.DataFrame.from_dict(df_dict)

        self.spotify_database.save_playlists_to_db(playlists_df)

    def __check_if_song_is_in_db(self):
        file = os.path.join(self.__PLAYLISTSPATH, "playlists_api.json")
        with open(file, 'r', encoding='UTF-8') as f:
            playlists = json.load(f)
        # test = self.spotify_database.is_track_in_db("2sdVNVVsrEoExbXhiItNuz")
        # print(test)
        ids_done = {}
        features = []
        for playlist in playlists:
            ids_to_do = []
            i=0
            for track in playlist['tracks']:
                try:
                    track_id = track['track']['id']
                except TypeError:
                    continue
                is_in_features = True if track_id in ids_done else False
                is_in_db = self.spotify_database.is_track_in_db(track_id)
                if not is_in_db and not is_in_features:
                    # if features:
                    i+=1
                    ids_done[track_id] = track['track']['name']
                    # ids_to_do.append(track_id)
                    # if i==10:
                    #     try:
                    #         features_to_do = self.get_single_track_features(ids_to_do)
                    #         if features_to_do:
                    #             features.extend(features_to_do)
                    #         else:
                    #             print("failed")
                    #             import time
                    #             time.sleep(60)
                    #             self.client = APIClient(self.username, self.id, self.secret)
                    #     except Exception as e:
                    #         print(e)
                    #     ids_to_do = []
                    #     i=0
                    # break
            # break
            if len(ids_to_do)>0:
                try:
                    features_to_do = self.get_single_track_features(ids_to_do)
                    if features_to_do:
                        features.extend(features_to_do)
                except Exception as e:
                    print(e)
        # with open(os.path.join(r"C:\Users\james\Documents\spotify\Features", "playlists_break08_11.json"), "w") as outfile:
        #     json.dump(features, outfile)
        all_features = {}
        with open(r"C:\Users\james\Documents\spotify\Features\playlists_break08_11.json", 'r', encoding='UTF-8') as f:
            features = json.load(f)
        import pickle
        # save pickle object with ids done
        fileObj = open(r"C:\Users\james\Documents\spotify\Features\ids_done.pkl", 'wb')
        pickle.dump(ids_done, fileObj)
        fileObj.close()
        fileObj = open(r"C:\Users\james\Documents\spotify\Features\ids_done.pkl", 'rb')
        ids_done = pickle.load(fileObj)
        fileObj.close()
        i=0
        for id, name in ids_done.items():
            if i>=len(features):
                break
            try:
                # found = False
                # while not found:
                if features[i]['id'] != id:
                    #     i+=1
                    # else:
                    #     found = True
                    print("false")
                    continue
                print("true")
                all_features[name] = features[i]
            except TypeError:
                continue
            i+=1
        with_features = []
        for track_name, features in all_features.items():
            with_features.append({'name': track_name, **features})
        return with_features

    def __get_playlists_songs(self):
        # not_found = ['37i9dQZF1DXdL58DnQ4ZqM', '37i9dQZF1DX3sZpm7aIEYp', '37i9dQZF1DXa28zjJKtGIV', '5oxHFqFU06ufRSZt8izJX6']
        # for id in not_found:
        #     try:
        #         results, tracks = self.client.get_playlist(id)
        #         print(results, tracks)
        #     except Exception as e:
        #         print(e)
        file = os.path.join(self.__PLAYLISTSPATH, "playlists.json")
        with open(file, 'r', encoding='UTF-8') as f:
            playlists = json.load(f)
        hrefs = []
        for key, val in playlists.items():
            hrefs.extend(list(val.values()))
        results_api = []
        for href in hrefs:
            try:
                results, tracks = self.client.get_playlist(href.split("/")[-1].split("?")[0])
                results['tracks'] = tracks
            except Exception as e:
                print(e)
                print(f"failed")
                continue
            results_api.append(results)
        with open(os.path.join(self.__PLAYLISTSPATH, "playlists_api.json"), "w") as outfile:
            json.dump(results_api, outfile)

    def __get_uri_from_artists_done(self, path) -> List[str]:
        features_done = self.__get_streams_done(path)
        feature_ids = []
        for feature_done in features_done:
            feature_ids.extend([f['name'] for f in feature_done[list(feature_done.keys())[0]]])
        # print(feature_ids)
        return feature_ids

    def __get_uri_from_streams_done(self, path) -> List[str]:
        """
        Look into the feature json files for ids that have been done. It helps
        whenever we have connection issues or access to Spotify API fails by
        preventing doing multiple API calls for same songs. Also sometimes API calls
        fail because you will have max retires reached, so just relaunch the code,
        it will change automatically your IP for you.

        :param path: the path of the feature directory
        :type path: str
        :return: the list of the uri where features have been accessed
        :rtype: List[str]
        """
        features_done = self.__get_streams_done(path)
        unique_ids = list(set([feature_done['uri']
                        for feature_done in features_done]))
        return unique_ids

    def __get_streams_done(self, path) -> List[dict]:
        """
        Look for files done in the database

        :param path: the path of the output folder
        :type path: str
        :return: the list of existing results
        :rtype: List[dict]
        """

        features_done: List[dict] = []
        json_files = [os.path.join(path, file) for file in
                      os.listdir(path)]
        for file in json_files:
            with open(file, 'r', encoding='UTF-8') as f:
                features_done.extend(json.load(f))
        return features_done

    def __get_streamings(self) -> List[dict]:
        """
        Gather all the streaming files into a single list containing all the single
        streaming dictionary.

        :param path: the path to the streaming files
        :type path: str
        :return: the list of the streamings
        :rtype: List[dict]
        """

        files = [os.path.join(self.__DATAPATH,  file) for file in
                 os.listdir(self.__DATAPATH) if file.endswith(".json")]
        all_streamings = []

        for file in files:
            with open(file, 'r', encoding='UTF-8') as f:
                new_streamings = json.load(f)
                all_streamings += [streaming for streaming
                                in new_streamings]

        return all_streamings

    def get_single_track_features(self, track):
        # try:
        #should uncomment if first time here
        # track_id = self.client.get_id(track)
        features = self.client.get_features(track)
        # print(f"{track} got")
        # except (spotipy.exceptions.SpotifyException,
        #         requests.exceptions.ProxyError):
        # except Exception as e:
        #     print(e)
        #     features = None
        #     print(f"{track} failed")
        return features

    def get_features_all_tracks(self, streamings: List[dict],
                            ids_done: List[dict], client: APIClient) -> List[dict]:
        """
        Get the track features of the streamings

        :param streamings: the list of all the streamings of the client
        :type streamings: List[dict]
        :param ids_done: the track' ids that have already been done
        :type ids_done: List[dict]
        :param client: the client accessing the API
        :type client: APIClient
        :return: the list of the track' features
        :rtype: List[dict]
        """
        WAITING_TIME = 0
        # get all information by tracknames
        unique_tracks = list(set([streaming['spotify_track_uri']
                        for streaming in streamings]))
        all_features = {}
        for track in tqdm(unique_tracks):
            if track not in ids_done:
                features = self.get_single_track_features(track)
                if features:
                    all_features[track] = features

        with_features = []
        for track_name, features in all_features.items():
            with_features.append({'name': track_name, **features})
        return with_features

    def get_artists(self, streamings: List[dict]) -> List[str]:
        return list(set(pd.DataFrame.from_records(streamings)
                        ['master_metadata_album_artist_name'].values))

    def ask_api_for_artists(self, artists: List[str], artists_done: List[str],
                            client: APIClient) -> List[dict]:
        """
        Get the artists summary via the API

        :param artists: the list of artists' names
        :type artists: List[str]
        :param artists_done: the artists that have already been found
        :type artists_done: List[str]
        :param client: the client accessing the API
        :type client: APIClient
        :return: the list of artists' information
        :rtype: List[dict]
        """
        # artists_and_related = []
        artist_infos = []
        for artist in tqdm(artists):
            if artist not in artists_done:
                try:
                    artist_id = client.get_artist_id(artist)
                    artist_infos.append(client.get_artist_infos(artist_id))
                    # related_artist = client.get_related_artists(artist_id)
                    # artists_and_related.append({artist: related_artist})
                except Exception as e:
                    print(e)
                    # print(f"{artist} failed")
                    continue
        return artist_infos #, artists_and_related

    def save_feature_data(self, path: str, features: List[dict], name = "features") -> None:
        """
        Save the data in the output folder

        :param path: the output path
        :type path: str
        :param features: the data to save
        :type features: List[dict]
        """
        # Writing data to JSON
        features_done = self.__get_streams_done(path)
        features_done.extend(features)
        with open(os.path.join(path, f"{name}.json"), "w") as outfile:
            json.dump(features, outfile)

if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--username', help="spotify username", required=True)
    # parser.add_argument('-i', '--id', help="client id", required=True)
    # parser.add_argument('-s', '--secret', help="client secret", required=True)
    # parser.add_argument('-d', '--database', help="postgresql username", required=True)
    # parser.add_argument('-p', '--password', help="postgresql password", required=True)
    # args = parser.parse_args()
    args = {}

    UpdateDatabase(args)