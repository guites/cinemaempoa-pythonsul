import sqlite3
import html2text

class StripToMarkdown:
    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file
        self._add_markdown_description_column()

    def _add_markdown_description_column(self):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE posts ADD COLUMN markdown_description TEXT")
        except sqlite3.OperationalError:
            pass
        conn.close()
    
    def strip_to_markdown(self):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, description FROM posts WHERE description IS NOT NULL")
        data = cursor.fetchall()
        h = html2text.HTML2Text()
        h.ignore_links = True
        for row in data:
            markdown_description = h.handle(row[1])
            cursor.execute("UPDATE posts SET markdown_description = ? WHERE id = ?", (markdown_description, row[0]))
        conn.commit()
        conn.close()
    
    def run(self):
        self.strip_to_markdown()

if __name__ == "__main__":
    strip_to_markdown = StripToMarkdown("cinebancarios.db")
    strip_to_markdown.run()