from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyLoader:

    def __init__(self, sp) -> None:
        self.sp = sp
        self.playlists = None
        self.saved_songs = None
        self.all_songs = []
        self.songs_details = []

    @classmethod
    def get_authorization(cls, scopes) -> 'SpotifyLoader':
        """
        Making authorization for user
        """
        load_dotenv('./utils/.env')
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        secret_key = os.getenv('SPOTIPY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URL')
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes, client_id=client_id, client_secret=secret_key, redirect_uri=redirect_uri))
        return cls(sp)

    def get_playlists(self) -> None:
        """
        Downloading user playlists
        """
        playlists = self.sp.current_user_playlists()
        self.playlists = [(playlist['name'], playlist['id']) for playlist in playlists['items']]

    def get_saved_songs(self) -> None:
        """
        Downloading user saved songs
        """
        songs = self.sp.current_user_saved_tracks(limit=50)
        self.saved_songs = [(song['track']['name'], song['track']['id']) for song in songs['items']]
        for song in self.saved_songs:
            self.all_songs.append(song[1])

    def get_all_songs_id(self, playlists, user_data=True) -> list:
        """
        create one variable for all songs in all playlists
        """
        all_songs = []
        if not playlists:
            playlists = self.all_songs
        for playlist_id in playlists:
            if user_data:
                playlist_id = playlist_id[1]
            playlist_items = self.sp.playlist_items(playlist_id)
            for song in playlist_items['items']:
                all_songs.append(song['track']['id'])
        return all_songs

    def get_details_about_songs(self, song_list) -> list:
        """
        Getting details about song
        """
        chunks = [song_list[i:i+100] for i in range(0, len(song_list), 100)]
        song_details = []
        for chunk in chunks:
            details = self.sp.audio_features(chunk)
            for detail in details:
                song_details.append({'danceability': detail['danceability'], 'energy': detail['energy'], 'key': detail['key'], 'loudness': detail['loudness'], 'mode': detail['mode'],
                                           'speechiness': detail['speechiness'], 'acousticness': detail['acousticness'], 'instrumentalness': detail['instrumentalness'],
                                           'liveness': detail['liveness'], 'valence': detail['valence'], 'tempo': detail['tempo'], 'duration_ms': detail['duration_ms'],
                                           'time_signature': detail['time_signature']})
        return song_details

    def get_songs_name(self, songs_id) -> list:
        """
        getting song name by id
        """
        songs_name = []
        for song_id in songs_id:
            songs_name.append(self.sp.track(song_id)['name'])
        return songs_name
        
    def get_playlist_name(self, playlist_id) -> str:
        playl = self.sp.playlist(playlist_id)
        return playl['name']

    def load_playlist(self, playlist_id) -> tuple:
        """
        getting details of song and their names        
        """
        all_songs_id = self.get_all_songs_id([playlist_id], user_data=False)
        all_songs_details = self.get_details_about_songs(all_songs_id)
        all_songs_name = self.get_songs_name(all_songs_id)
        return all_songs_details, all_songs_name, all_songs_id

    def run(self) -> None:
        """
        running functions to get all informations about user
        """
        self.get_playlists()
        self.get_saved_songs()

    def run_for_details(self) -> None:
        """
        running functions to get detailed info abouts songs
        """
        self.all_songs = self.get_all_songs_id(self.playlists)
        self.songs_details = self.get_details_about_songs(self.all_songs)

