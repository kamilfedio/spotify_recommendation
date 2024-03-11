from spotify_loader import SpotifyLoader
from recomendation_engine import RecommendationEngine

class ManageRecommendation:
    def __init__(self) -> None:
        self.spotify_loader = None
        self.recommendation_engine = None

    def authorize_spotify(self, scopes) -> None:
        self.spotify_loader = SpotifyLoader.get_authorization(scopes)

    def load_data(self) -> None:
        if self.spotify_loader is not None:
            self.spotify_loader.run()

    def load_data_for_recomendation(self) -> None:
        if self.spotify_loader is not None:
            self.spotify_loader.run_for_details()

    def create_recommendation_engine(self) -> None:
        song_details = self.spotify_loader.songs_details
        if len(song_details) > 0:
            self.recommendation_engine = RecommendationEngine.load_data_from_user(song_details)
        else:
            return None

    def train_recommendation_engine(self) -> None:
        if self.recommendation_engine is not None:
            self.recommendation_engine.train_engine()
        else:
            return None
        
    def make_predictions(self, playlist_id) -> tuple:
        if self.recommendation_engine is not None:
            songs_details, songs_name, songs_ids = self.spotify_loader.load_playlist(playlist_id)
            pred = self.recommendation_engine.make_predictions(songs_details)
            playlist_name = self.spotify_loader.get_playlist_name(playlist_id)
            return (pred, songs_name, playlist_name)

    def logout(self) -> None:
        import os
        try:
            os.remove('.cache')
        except:
            pass
    @property
    def playlists(self):
        if self.spotify_loader is not None:
            return self.spotify_loader.playlists
        else:
            return None   