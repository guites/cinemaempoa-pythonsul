import sqlite3
from datetime import datetime
import os
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.core.bridge.pydantic import BaseModel


class Movie(BaseModel):
    title: str
    image_url: str
    general_info: str
    director: str
    classification: str
    excerpt: str
    screening_dates: list[str]

class Movies(BaseModel):
    movies: list[Movie]

class ExtractScreeningsFromMarkdown:
    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file
        self.llm = GoogleGenAI(model="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY"))
        Settings.llm = self.llm
    
    def extract_screenings_from_markdown(self):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, link, pubDate, markdown_description FROM posts WHERE markdown_description IS NOT NULL AND id = 638 ORDER BY pubDate ASC")
        data = cursor.fetchall()
        for row in data:
            # pubDate is in the format 2010-03-09T18:48:00+00:00
            pubDate = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S+00:00")
            year = pubDate.year
            markdown_description = row[3]
            link = row[1]
            response = self.llm.as_structured_llm(Movies).chat(self._get_prompt(year, markdown_description))
            print(link)
            print(response)
            break
    
    def _get_prompt(self, year, text_content):
        messages = [
            ChatMessage(
                role="system",
                content=f"""You are a cinema programming auditor. You need to collect screening information from the following text.
For each movie, extract the following information:
1. Title: The name of the movie
2. Image URL: If available, the URL of the movie's poster image
3. General Info: Information in the format "Country/Genre/Year/Duration" (e.g. "Brasil/Drama/2023/97min")
4. Director: The director's name, usually found after "Direção:"
5. Classification: The age rating, usually found after "Classificação indicativa:"
6. Excerpt: The movie's synopsis, usually found after "Sinopse:"
7. Screening Dates: All dates and times when the movie is shown
The text may contain multiple movies. Each movie's information is usually separated by blank lines or section headers like "ESTREIA" or "EM CARTAZ".
Make sure to:
- Extract all available information for each movie
- Handle cases where some information might be missing
- Keep the original formatting of the text where appropriate
- Include all screening times for each movie. The year is {year}. The format of the dates is YYYY-MM-DD HH:MM.
- Return the data in JSON format that matches the following structure:

If no movies are found, return an empty list."""
            ),
            ChatMessage(
                role="user",
                content=text_content
            )
        ]
        return messages
    
    def run(self):
        self.extract_screenings_from_markdown()

if __name__ == "__main__":
    extract_screenings_from_markdown = ExtractScreeningsFromMarkdown("cinebancarios.db")
    extract_screenings_from_markdown.run()