import sqlite3
import csv

conn = sqlite3.connect('./utils/dane_muzyczne.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS songs
                  (id INTEGER PRIMARY KEY,
                   danceability REAL,
                   energy REAL,
                   key INTEGER,
                   loudness REAL,
                   mode INTEGER,
                   speechiness REAL,
                   acousticness REAL,
                   instrumentalness REAL,
                   liveness REAL,
                   valence REAL,
                   tempo REAL,
                   duration_ms INTEGER,
                   time_signature INTEGER,
                    liked INTEGER)''')

with open('./utils/false_data.csv', 'r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader) 
    for row in csv_reader:
        cursor.execute('''INSERT INTO songs 
                          (danceability, energy, key, loudness, mode, speechiness,
                           acousticness, instrumentalness, liveness, valence, 
                           tempo, duration_ms, time_signature, liked) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)

conn.commit()
conn.close()
