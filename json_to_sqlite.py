import json
import sqlite3
import os
from datetime import datetime

class JsonToSqlite:
    def __init__(self, json_file, sqlite_file):
        self.sqlite_file = sqlite_file
        self.json_file = json_file

    def load_json(self):
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        return data
    
    def create_table(self):
        conn = sqlite3.connect(self.sqlite_file)
        conn.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, link TEXT, pubDate DATETIME, description TEXT, author TEXT, scraped_at DATETIME)''')
        conn.close()
    
    def insert_data(self, data):
        conn = sqlite3.connect(self.sqlite_file)
        # Prepare data for executemany - convert list of dicts to list of tuples
        data_tuples = [(item["title"], item["link"], item["pubDate"], item["description"], item["author"], item["scraped_at"]) for item in data]
        conn.executemany('INSERT INTO posts (title, link, pubDate, description, author, scraped_at) VALUES (?, ?, ?, ?, ?, ?)', data_tuples)
        conn.commit()
        conn.close()
    
    def run(self):
        self.create_table()
        self.data = self.load_json()
        self.insert_data(self.data)

if __name__ == "__main__":
    json_to_sqlite = JsonToSqlite("sorted.json", "cinebancarios.db")
    json_to_sqlite.run()