import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestClassifier

class RecommendationEngine:

    def __init__(self, song_details, song_details_2) -> None:
        self.song_details = song_details
        self.no_liked_song = song_details_2
        self.model = None

    @classmethod
    def load_data_from_user(cls, songs_details) -> 'RecommendationEngine':
        details = [list(song.values()) for song in songs_details]
        columns = list(songs_details[0].keys())
        df = pd.DataFrame(data=details, columns=columns)
        conn = sqlite3.connect('./utils/dane_muzyczne.db')
        df2 = pd.read_sql_query('SELECT * FROM songs', conn)
        return cls(df, df2)

    
    def train_engine(self) -> None:
        self.no_liked_song['liked'] = 0
        self.song_details['liked'] = 1
        df = pd.concat([self.no_liked_song, self.song_details], ignore_index=True)
        df.drop(columns=['id'], inplace=True)
        target = df.pop('liked')

        self.model = RandomForestClassifier()
        self.model.fit(df, target)

    def proceess_predict_data(self, data) -> pd.DataFrame:
        details = [list(song.values()) for song in data]
        columns = list(data[0].keys())
        df = pd.DataFrame(data=details, columns=columns)
        return df

    def make_predictions(self, data) -> list:
        df = self.proceess_predict_data(data)
        predicts = self.model.predict(df)
        return predicts

    def run_engine(self) -> None:
        self.train_engine()
