import sqlite3
import json
import os
class ExportPostJson:
    def __init__(self, directory, sqlite_file):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.sqlite_file = sqlite_file

    def export_post_json(self):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
        p.id,
        json_group_array(
            json_object(
            'title', p.title,
            'link', p.link,
            'pubDate', p.pubDate,
            'llm', l.llm,
            'output', json(l.output)
            )
        ) AS extracted_json
        FROM posts p
        LEFT JOIN llm_outputs l ON p.id = l.post_id
        WHERE l.output IS NOT NULL
        GROUP BY p.id;
        """)
        posts = cursor.fetchall()
        for post in posts:
            loaded = json.loads(post[1])
            os.makedirs(os.path.join(self.directory, f"{post[0]}"), exist_ok=True)
            for item in loaded:
                with open(os.path.join(self.directory, f"{post[0]}", f"{item['llm']}.json"), "w") as f:
                    json.dump(item, f, indent=2)
        conn.close()

if __name__ == "__main__":
    export_post_json = ExportPostJson("posts", "cinebancarios.db")
    export_post_json.export_post_json()