import ast
import os
from typing import List
import json
import spotipy
import spotipy.util as util
import requests
import math
import time
from tqdm import tqdm
import pandas as pd
from matplotlib import pylab
import matplotlib.pyplot as plt
import networkx as nx

# from https://stackoverflow.com/questions/70852145/avoiding-429-is-there-a-way-to-incorporate-spotify-api-retry-after-response
# from bs4 import BeautifulSoup
# import requests

# def GetProxys():
#     website_html = requests.get("https://free-proxy-list.net").text
#     soup = BeautifulSoup(website_html, "html.parser")
#     soup = soup.find("table")
#     Headings = []
#     Body = []
#     Ip = []
#     for heading in soup.find_all("th"):
#         Headings.append(heading.text)
#     for ip_html in soup.find_all("tr"):
#         ip_info_list = []
#         for ip_info in ip_html.find_all("td"):
#             ip_info_list.append(ip_info.text)
#         if len(ip_info_list) > 1:
#             if ip_info_list[6] == "yes":
#                 Ip.append(f"{ip_info_list[0]}:{ip_info_list[1]}")
#                 Body.append(ip_info_list)
#     return Ip

# def perform_request(ip):
#     http_proxy = f"http://{ip}"
#     https_proxy = f"https://{ip}"

#     proxyDict = {
#         "http": http_proxy,
#         "https": https_proxy,
#     }
#     try:
#        r = requests.get("http://api.ipify.org",
#                              proxies=proxyDict, timeout=10)
#        print(f"{r}/{r.text}", end="/")
#     except:
#         print("{-_-}", end="/")
#     print()

MYPATH = ".\MyData"
WAITING_TIME = 0

def get_features(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([track_id])
        return features[0]
    except spotipy.exceptions.SpotifyException:
        raise
    except:
        return None

def get_related_artists(artist_dic: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.artist_related_artists(artist_dic['id'])
        return features['artists']
    except spotipy.exceptions.SpotifyException:
        raise
    except:
        raise
        # return None

def get_id(track_name: str, token: str) -> str:
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer ' + token,
    }
    params = [
    ('q', track_name),
    ('type', 'track'),
    ]

    try:
        response = requests.get('https://api.spotify.com/v1/search',
                    headers = headers, params = params, timeout = 10)
        json = response.json()
        first_result = json['tracks']['items'][0]
        track_id = first_result['id']
        return track_id
    except:
        print("failed id")
        raise

def get_token() -> str:
    username = ''
    client_id =''
    client_secret = ''
    redirect_uri = 'http://localhost:7777/callback'
    scope = 'user-read-recently-played'

    token = util.prompt_for_user_token(username=username,
                                    scope=scope,
                                    client_id=client_id,
                                    client_secret=client_secret,
                                    redirect_uri=redirect_uri)
    return token

def get_streamings(path: str = 'MyData') -> List[dict]:

    files = [os.path.join(path,  x) for x in os.listdir(path)
             if not ".pdf" in x and not "Video" in x]

    all_streamings = []

    for file in files:
        with open(file, 'r', encoding='UTF-8') as f:
            new_streamings = json.load(f)
            all_streamings += [streaming for streaming
                               in new_streamings]
    return all_streamings

def get_features_all_tracks(streamings: List[dict], ids_done: List[dict]) -> List[dict]:
    global WAITING_TIME
    # get all informations by tracknames
    unique_tracks = list(set([streaming['master_metadata_track_name']
                    for streaming in streamings]))

    all_features = {}
    for track in unique_tracks:
        # time.sleep(WAITING_TIME)
        # no_proxy_answer = True
        # while no_proxy_answer:
        token = get_token()
        try:
            track_id = get_id(track, token)
            if track_id in ids_done:
                features = None
                print("already done")
            else:
                features = get_features(track_id, token)
                print("got")
                # no_proxy_answer = False
            # except (spotipy.exceptions.SpotifyException,
            #         requests.exceptions.ProxyError):
        except:
            features = None
            print(f"{track} failed")
                # WAITING_TIME+=30
                # time.sleep(30)
                # print("waiting")
                # # print(track)
                # # features = None
                # # no_proxy_answer = False
        if features:
            all_features[track] = features

    with_features = []
    for track_name, features in all_features.items():
        with_features.append({'name': track_name, **features})
    return with_features

def save_feature_data(features: List[dict], i:str = None) -> None:
    # Writing data to JSON
    with open(f"james_artists.json", "w") as outfile:
        json.dump(features, outfile)

def look_for_streams_done():
    features_done: List[dict] = []
    JSON_PATH = r""
    json_files = [file for file in os.listdir(JSON_PATH) if "james_features_total_final_cestbon.json" in file]
    for file in json_files:
        with open(file, 'r', encoding='UTF-8') as f:
            features_done.extend(json.load(f))
    unique_ids = list(set([feature_done['id']
                    for feature_done in features_done]))
    return unique_ids

def regroup_features():
    features_done: List[dict] = []
    JSON_PATH = r""
    json_files = [file for file in os.listdir(JSON_PATH) if "james_features" in file]
    for file in json_files:
        with open(file, 'r', encoding='UTF-8') as f:
            features_done.extend(json.load(f))
    print(len(features_done))
    features_done_unique = [dict(t) for t in {tuple(d.items()) for d in features_done}]
    print(len(features_done_unique))
    with open(f"james_features_total_final_cestbon_final_1.json", "w") as outfile:
        json.dump(features_done_unique, outfile)

def compare_features_with_streams(streamings: List[dict]):
    with open("james_features_total_final_cestbon_final_1.json", 'r', encoding='UTF-8') as f:
        features_done = json.load(f)
    streamings_ids = list(set([streaming['spotify_track_uri']
                    for streaming in streamings]))
    not_founds = []
    for streaming_id in streamings_ids:
        found = False
        for feature_done in features_done:
            try:
                if streaming_id.split(":")[-1] == feature_done['id']:
                    found = True
                    break
            except AttributeError:
                break
        if not found:
            # print(streaming_id['master_metadata_track_name'])
            not_founds.append(streaming_id)
    streamings_not_found = []
    for not_found in not_founds:
        for streaming in streamings:
            if streaming['spotify_track_uri'] == not_found:
                streamings_not_found.append(streaming)
                break
    return streamings_not_found

def get_artist_id(artist_name: str, token: str) -> str:
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer ' + token,
    }
    params = [
    ('q', artist_name),
    ('type', 'artist'),
    ]

    try:
        response = requests.get('https://api.spotify.com/v1/search',
                    headers = headers, params = params, timeout = 10)
        # response = requests.get('https://api.spotify.com/v1/search',
        #             proxies=proxyDict, params = params, timeout = 5)
        json = response.json()
        best_result = None
        best_popularity = 0
        for result in json['artists']['items']:
            if result['name'] == artist_name and result['popularity'] > best_popularity:
                best_popularity = result['popularity']
                best_result = result
        return best_result
    except:
        print("failed id")
        raise
        # return None

def get_artists(streamings):
    return list(set(pd.DataFrame.from_records(streamings)['master_metadata_album_artist_name'].values))

def ask_api_for_artists(artists: List[str]):
    artists_and_related = []
    for artist in artists:
        try:
            token = get_token()
            artist_dic = get_artist_id(artist, token)
            related_artist = get_related_artists(artist_dic, token)
            artists_and_related.append({artist: related_artist})
        except:
            print(f"{artist} failed")
            continue
    return artists_and_related

# https://stackoverflow.com/questions/17381006/large-graph-visualization-with-python-and-networkx
def save_graph(graph,file_name):
    #initialze Figure
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph,pos)
    nx.draw_networkx_edges(graph,pos)
    nx.draw_networkx_labels(graph,pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.savefig(file_name,bbox_inches="tight")
    pylab.close()
    del fig

def create_graph(artists: List[dict]):
    G = nx.Graph()
    artist_names = [list(artist.keys())[0] for artist in artists]
    # G.add_nodes_from(artist_names)
    artists_done = []
    for artist in artists:
        for related_artist in list(artist.values())[0]:
            if related_artist['name'] in artist_names:
                if related_artist['name'] not in artists_done:
                    G.add_node(related_artist['name'])
                    artists_done.append(related_artist['name'])
                if list(artist.keys())[0] not in artists_done:
                    G.add_node(list(artist.keys())[0])
                    artists_done.append(list(artist.keys())[0])
                G.add_edge(list(artist.keys())[0], related_artist['name'])
    # too much for viz
    remove = [node for node,degree in dict(G.degree()).items() if degree < 50]
    G.remove_nodes_from(remove)
    return G

def main():
    # # ids_done = look_for_streams_done()
    # # # # don't get all at once, because you will have max retires reached -> not because of IP but rate limit
    # streamings = get_streamings(MYPATH) # remove [0:5] for all
    # # # # print(len(streamings))
    # # # # for streaming in streamings:
    # # # #     for stream_done in streams_done:
    # # # #         if streaming['spotify_track_uri'] == stream_done['uri']:
    # # # #             print("found")
    # # # #             import pdb
    # # # #             pdb.set_trace()
    # # # # import pdb
    # # # # pdb.set_trace()
    # # # # ips = GetProxys()
    # # # divide_len= 100000
    # # # for i in tqdm(range(math.ceil(len(streamings)/divide_len))):
    # # #     james_features = get_features_all_tracks(streamings[divide_len*i:max(divide_len*(i+1), len(streamings)-1)], ids_done)
    # # #     # print(james_features)
    # # #     save_feature_data(james_features, i)
    # # #     print("saved")
    # # # regroup_features()
    # # streamings_not_found = compare_features_with_streams(streamings)
    # # # import pdb
    # # # pdb.set_trace()
    # # added_features = get_features_all_tracks(streamings_not_found, ids_done)
    # # save_feature_data(added_features, 20)
    # artists = get_artists(streamings)
    # # import pdb
    # # pdb.set_trace()
    # # artists = ['Worakls']
    # artists_and_related = ask_api_for_artists(artists)
    # save_feature_data(artists_and_related, 0)
    with open('james_artists.json', 'r', encoding='UTF-8') as f:
        artists = json.load(f)
    artist_graph = create_graph(artists)
    save_graph(artist_graph,"my_graph.pdf")
    nx.write_edgelist(artist_graph, "my_graph.csv", delimiter = ";", data=False)

if __name__ == "__main__":
    main()