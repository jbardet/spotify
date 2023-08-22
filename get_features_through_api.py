import os
import json
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util
import argparse
import pandas as pd
from tqdm import tqdm

class APIClient:
    def __init__(self, username: str, id: str, secret: str):
        self.__username = username
        self.__id = id
        self.__secret = secret
        self.__token = self.__getToken()
        self.__ips = self.__getProxys()

    def __getToken(self) -> str:

        redirect_uri = 'http://localhost:7777/callback'
        scope = 'user-read-recently-played'

        token = util.prompt_for_user_token(username=self.__username,
                                        scope=scope,
                                        client_id=self.__id,
                                        client_secret=self.__secret,
                                        redirect_uri=redirect_uri)
        return token

    def __getProxys(self) -> str:
        """
        Get a Proxy IP address so that Spotify does not block your number of API
        calls through your IP address
        Adapted from:
        https://stackoverflow.com/questions/70852145/avoiding-429-is-there-a-way-to-incorporate-spotify-api-retry-after-response

        :return: the new IP address
        :rtype: str
        """
        website_html = requests.get("https://free-proxy-list.net").text
        soup = BeautifulSoup(website_html, "html.parser")
        soup = soup.find("table")
        Headings = []
        Body = []
        Ip = []
        for heading in soup.find_all("th"):
            Headings.append(heading.text)
        for ip_html in soup.find_all("tr"):
            ip_info_list = []
            for ip_info in ip_html.find_all("td"):
                ip_info_list.append(ip_info.text)
            if len(ip_info_list) > 1:
                if ip_info_list[6] == "yes":
                    Ip.append(f"{ip_info_list[0]}:{ip_info_list[1]}")
                    Body.append(ip_info_list)
        return Ip

    def __call_api(self, params: List[Tuple], name: str):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer ' + self.__token,
        }

        try:
            response = requests.get('https://api.spotify.com/v1/search',
                        headers = headers, params = params, timeout = 10)
            json = response.json()
            first_result = json[name]['items'][0]
            # track_id = first_result['id']
            return first_result
        except:
            # print("failed")
            raise

    def get_artist_id(self, artist_name: str) -> str:
        params = [
        ('q', artist_name),
        ('type', 'artist'),
        ]
        artist = self.__call_api(params, 'artists')
        return artist['id']

    def get_id(self, track_name: str) -> str:
        params = [
        ('q', track_name),
        ('type', 'track'),
        ]
        feature = self.__call_api(params, 'tracks')
        return feature['id']

    def get_related_artists(self, artist_id: str) -> dict:
        sp = spotipy.Spotify(auth=self.__token)
        try:
            features = sp.artist_related_artists(artist_id)
            return features['artists']
        except spotipy.exceptions.SpotifyException:
            raise
        except:
            raise
            # return None

def get_streams_done(path: str) -> List[dict]:
    """
    Look for files done in the output folder

    :param path: the path of the output folder
    :type path: str
    :return: the list of existing results
    :rtype: List[dict]
    """

    features_done: List[dict] = []
    json_files = [os.path.join(path, file) for file in os.listdir(path)]
    for file in json_files:
        with open(file, 'r', encoding='UTF-8') as f:
            features_done.extend(json.load(f))
    return features_done

def get_uri_from_streams_done(path: str) -> List[str]:
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
    features_done = get_streams_done(path)
    unique_ids = list(set([feature_done['uri']
                    for feature_done in features_done]))
    return unique_ids

def get_artists(streamings: List[dict]) -> List[str]:
    return list(set(pd.DataFrame.from_records(streamings)
                    ['master_metadata_album_artist_name'].values))

def get_streamings(path: str) -> List[dict]:
    """
    Gather all the streaming files into a single list containing all the single
    streaming dictionary.

    :param path: the path to the streaming files
    :type path: str
    :return: the list of the streamings
    :rtype: List[dict]
    """

    files = [os.path.join(path,  file) for file in os.listdir(path)
             if file.endswith(".json")]
    all_streamings = []

    for file in files:
        with open(file, 'r', encoding='UTF-8') as f:
            new_streamings = json.load(f)
            all_streamings += [streaming for streaming
                               in new_streamings]

    return all_streamings

def ask_api_for_artists(artists: List[str], artists_done, client) -> List[dict]:
    artists_and_related = []
    for artist in artists:
        if artist not in artists_done:
            try:
                artist_dic = client.get_artist_id(artist)
                related_artist = client.get_related_artists(artist_dic)
                artists_and_related.append({artist: related_artist})
            except Exception as e:
                print(e)
                print(f"{artist} failed")
                continue
    return artists_and_related

def get_features(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([track_id])
        return features[0]
    except spotipy.exceptions.SpotifyException:
        raise
    except:
        return None

def get_features_all_tracks(streamings: List[dict],
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
            try:
                track_id = client.get_id(track)
                features = get_features(track_id)
                # print(f"{track} got")
            # except (spotipy.exceptions.SpotifyException,
            #         requests.exceptions.ProxyError):
            except:
                features = None
                # print(f"{track} failed")
            if features:
                all_features[track] = features

    with_features = []
    for track_name, features in all_features.items():
        with_features.append({'name': track_name, **features})
    return with_features

def save_feature_data(path: str, features: List[dict]) -> None:
    """
    Save the data in the output folder

    :param path: the output path
    :type path: str
    :param features: the data to save
    :type features: List[dict]
    """
    # Writing data to JSON
    features_done = get_streams_done(path)
    features_done.extend(features)
    with open(os.path.join(path, "features.json"), "w") as outfile:
        json.dump(features, outfile)

def main(args: dict):
    """

    :param username: the username to access spotify API
    :type username: str
    :param id: the user id to access spotify API
    :type id: str
    :param secret: the user secret id to access spotify API
    :type secret: str
    """

    client = APIClient(args.username, args.id, args.secret)
    BASEPATH = os.path.dirname(os.path.realpath(__file__))
    DATAPATH = os.path.join(BASEPATH, "MyData")

    # directory where the feature information accessed through API will lie
    FEATURESPATH = os.path.join(BASEPATH, "Features")
    if not os.path.isdir(FEATURESPATH):
        os.mkdir(FEATURESPATH)
        ids_done = []
    else:
        ids_done = get_uri_from_streams_done(FEATURESPATH)

    streamings = get_streamings(DATAPATH)
    try:
        features = get_features_all_tracks(streamings, ids_done, client)
    except Exception as e:
        print(e)
        raise
    save_feature_data(FEATURESPATH, features)

    ARTISTSPATH = os.path.join(BASEPATH, "Artists")
    if not os.path.isdir(ARTISTSPATH):
        os.mkdir(ARTISTSPATH)
        artists_done = []
    else:
        artists_done = get_uri_from_streams_done(ARTISTSPATH)
    artists = get_artists(streamings)
    artists_and_related = ask_api_for_artists(artists, artists_done, client)
    save_feature_data(ARTISTSPATH, artists_and_related)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help="spotify username", required=True)
    parser.add_argument('-i', '--id', help="client id", required=True)
    parser.add_argument('-s', '--secret', help="client secret", required=True)
    args = parser.parse_args()

    main(args)