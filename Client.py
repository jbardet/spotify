import spotipy.util as util
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
import spotipy
import time
import concurrent.futures
import webbrowser
import time

class APIClient:
    def __init__(self, usernames: List[str], ids: List[str], secrets: List[str]):
        self.__usernames = usernames
        self.__ids = ids
        self.__secrets = secrets
        assert len(self.__usernames) == len(self.__ids), "not same length"
        assert len(self.__usernames) == len(self.__secrets), "not same length"
        self.__max_workers = len(self.__usernames)  # Number of parallel requests
        self.__tokens = self.__getToken()
        self.__ips = self.__getProxys()
        self.sp = spotipy.Spotify(auth=self.__tokens[0])

    def refresh_token(self):
        self.__tokens = self.__getToken()
        self.sp = spotipy.Spotify(auth=self.__tokens[0])

    def __getToken(self) -> str:

        redirect_uri = 'http://localhost:7777/callback'
        scope = 'playlist-modify playlist-modify-private user-read-recently-played user-library-read user-read-currently-playing user-read-playback-state user-modify-playback-state'
        tokens = []
        for i in range(self.__max_workers):
            try:
                token = util.prompt_for_user_token(username=self.__usernames[i],
                                                scope=scope,
                                                client_id=self.__ids[i],
                                                client_secret=self.__secrets[i],
                                                redirect_uri=redirect_uri)
                tokens.append(token)
            except spotipy.oauth2.SpotifyOauthError:
                tokens.append(None)
        return tokens

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

    def create_playlist(self, songs, name):
        """
        Uses spotipy to create a Spotify playlist with the songs and name given

        :param songs: _description_
        :type songs: _type_
        :param name: _description_
        :type name: _type_
        """
        self.sp.user_playlist_create(user=self.__usernames[0], name=name)
        playlists = self.sp.user_playlists(self.__usernames[0])

        pl = list(playlists['items'])[0]

        # print(pl['id'], '\t', pl['name'], '\t', pl['tracks']['total'])

        self.sp.user_playlist_add_tracks(self.__usernames[0], pl['id'], tracks = songs)

        self.start_playing_playlist(self.sp, pl)

        time.sleep(5)
        self.sp.current_user_unfollow_playlist(pl['id'])

        # print(pl['id'], '\t', pl['name'], '\t', pl['tracks']['total'])

    def play_playlist(self, pl):
        self.start_playing_playlist(pl)

    def start_playing_playlist(self, pl):
        """
        Start playing a playlist via Spotipy

        :param playlist_id: _description_
        :type playlist_id: _type_
        """
        # webbrowser.open(pl['uri'])
        try:
            playlist_id = pl['uri']
        except (KeyError, TypeError):
            playlist_id = 'spotify:playlist:'+pl
        self.sp.start_playback(context_uri=playlist_id)

    def play(self, device_id: str = None):
        if device_id:
            try:
                self.sp.start_playback(device_id=device_id)
            except spotipy.exceptions.SpotifyException:
                raise
        try:
            self.sp.start_playback()
        except spotipy.exceptions.SpotifyException:
            raise

    def pause(self, device_id: str = None):
        if device_id:
            try:
                self.sp.pause_playback(device_id=device_id)
            except spotipy.exceptions.SpotifyException:
                raise
        try:
            self.sp.pause_playback()
        except spotipy.exceptions.SpotifyException:
            raise

    def next(self, device_id: str = None):
        if device_id:
            try:
                self.sp.next_track(device_id=device_id)
            except spotipy.exceptions.SpotifyException:
                raise
        try:
            self.sp.next_track()
        except spotipy.exceptions.SpotifyException:
            raise

    def previous(self, device_id: str = None):
        if device_id:
            try:
                self.sp.previous_track(device_id=device_id)
            except spotipy.exceptions.SpotifyException:
                raise
        try:
            self.sp.previous_track()
        except spotipy.exceptions.SpotifyException:
            raise

    def shuffle(self):
        try:
            self.sp.shuffle(state=True)
        except spotipy.exceptions.SpotifyException:
            raise

    def get_current_track(self, device_id: str = None):
        try:
            return self.sp.current_user_playing_track()
        except spotipy.exceptions.SpotifyException as e:
            if "The access token expired" in e.msg:
                self.refresh_token()
                return self.sp.current_user_playing_track()

    def __call_api(self, params: List[Tuple], name: str = None, type: str = 'search'):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer ' + self.__tokens[0],
        }

        http_proxy = f"http://{self.__ips[-1]}"
        https_proxy = f"https://{self.__ips[-1]}"

        proxyDict = {
            "http": http_proxy,
            "https": https_proxy,
        }
        while len(self.__ips)>0:
            try:
                response = requests.get('https://api.spotify.com/v1/' + type,
                            headers = headers, proxies=proxyDict, params = params, timeout = 10)
                json = response.json()
                first_result = json[name]['items'][0]
                # track_id = first_result['id']
                print("success")
                return first_result
            except Exception as e:
                print(e)
                print("failed")
                self.__ips.pop()
                # raise

    def get_devices(self):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer ' + self.__tokens[0],
        }
        response = requests.get('https://api.spotify.com/v1/me/player/devices',
                            headers = headers)
        return response.json()
        # params = [
        # ('q', 'devices'),
        # ('type', 'player'),
        # ]
        # return self.__call_api(params, 'player', type="me")

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
        try:
            features = self.sp.artist_related_artists(artist_id)
            return features['artists']
        except spotipy.exceptions.SpotifyException:
            raise
        except:
            raise
            # return None

    def get_playlist(self, playlist_href: str):
        results = self.sp.playlist(playlist_href)
        del results['tracks']
        tracks_response = self.sp.playlist_tracks(playlist_href)
        tracks = tracks_response["items"]
        while tracks_response["next"]:
            tracks_response = self.sp.next(tracks_response)
            tracks.extend(tracks_response["items"])

        return results, tracks
        # sp = spotipy.Spotify(auth=self.__token)
        # results = sp.playlist(playlist_href)
        # # we have to do this because limit is 100 songs per playlist
        # tracks = results['tracks']
        # while results['next']:
        #     results = sp.next(results)
        #     tracks.extend(results['tracks'])
        # other_key = ['collaborative', 'description', 'external_urls', 'followers',
        #              'href', 'id', 'images', 'name', 'owner', 'primary_color',
        #              'public', 'snapshot_id', 'type', 'uri']
        # return results[other_key], tracks

        # params = [
        # ('q', playlist_href),
        # ('type', 'playlist'),
        # ]
        # feature = self.__call_api(params, 'tracks')
        # print(feature)
        # return feature

    def get_features(self, track_ids: List[str]) -> dict:
        # sp = spotipy.Spotify(auth=self.__token)# , requests_timeout=10, retries=10)
        # try:
        #     features = sp.audio_features(track_ids[0])
        # except Exception as e:
        #     print(e)
        # features = []
        # for track_id in track_ids:
        try:
            # features = sp.audio_features(track_ids)
            # features = self._get("audio-features/?ids=" + trackid)
            feature = self.ask_api("features", track_ids)
            # if feature:
            #     features.append(feature)
            # return features
            # time.sleep(10)
        except spotipy.exceptions.SpotifyException as e:
            # raise
            print(e)
        # except Exception as e:
            # return None
            # print(e)
        return feature

    def __call_features(self, token, id):
        http_proxy = f"http://{self.__ips[-1]}"
        https_proxy = f"https://{self.__ips[-1]}"

        proxyDict = {
            "http": http_proxy,
            "https": https_proxy,
        }
        while len(self.__ips)>0:
            headers = {
                # 'Accept': 'application/json',
                # 'Content-Type': 'application/json',
                'Authorization': f'Bearer ' + token
                # 'Retry-After': '4',
            }
            # while True:
            time.sleep(10)
            try:
                response = requests.get('https://api.spotify.com/v1/audio-features/'+ id,
                            headers=headers, timeout = 10) #proxies=proxyDict,
                json = response.json()
                print(json, token, id)
                # print(token)
                # print(id)
                if 'error' not in json.keys():
                    first_result = json
                    # track_id = first_result['id']
                    print("success")
                    return first_result
                else:
                    if json['error']['status'] !=429:
                        return None
                    else:
                        print("error, wait", json)
                        # time.sleep(6000)
                        # self.tokens = self.__getToken()
                        # token = self.tokens[0]
                        return None
            except Exception as e:
                print(e, id)
                # print(f"{id, self.__ips[-1]} failed")
                # from time import sleep
                # sleep(30)
                self.__ips.pop()
                raise

    def ask_api(self, option, ids):
        results = []  # List to store the results
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.__max_workers) as executor:
            # Use list comprehension to submit tasks for each account
            if option == "features":
                for token in self.__tokens:
                    for id in ids:
                        print(token, id)
                        # middle_point = int(len(ids)/self.__max_workers)
                        # print(ids)
                        # id = ids[i * middle_point:(i + 1) * middle_point]
                        # print(id)
                        # id = ids[2*i]
                        # Use list comprehension to submit tasks for each account in the group
                        # Provide both parameters (token and id) to the fetch_account_data function
                        future_to_token = {
                            executor.submit(self.__call_features, token, id)
                        }
                        # future_to_account = {executor.submit(self.__call_features, id, token): token for token in self.__tokens}
                        # Iterate through the completed tasks
                        for future in concurrent.futures.as_completed(future_to_token):
                            # account = future_to_token[future]
                            # print("account")
                            try:
                                data = future.result()
                                if not data:
                                    return results
                                results.append(data)  # Append the result to the list
                                # print("appended")
                                # print(f"Data for {account}: {data}")
                            except Exception as e:
                                print(f"Error fetching data for: {e}")
        return results