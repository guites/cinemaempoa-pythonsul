import sqlite3
from datetime import datetime
import os
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.core.bridge.pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
import time
from google.genai.errors import ClientError as GoogleGenAIClientError
import sys

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SQLITE_FILE = os.getenv("SQLITE_FILE")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

if not SQLITE_FILE:
    raise ValueError("SQLITE_FILE is not set")


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
    def __init__(self):
        self.model_name = "gemini-2.0-flash"
        self.sqlite_file = SQLITE_FILE
        self.llm = GoogleGenAI(model=self.model_name, api_key=GEMINI_API_KEY)
        Settings.llm = self.llm
    
    def extract_screenings_from_markdown(self):
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.link, p.pubDate, p.markdown_description
            FROM posts p LEFT JOIN llm_outputs l ON p.id = l.post_id
            WHERE p.markdown_description IS NOT NULL AND l.id IS NULL
            ORDER BY pubDate ASC
        """)
        data = cursor.fetchall()
        for row in data:
            # pubDate is in the format 2010-03-09T18:48:00+00:00
            pubDate = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S+00:00")
            year = pubDate.year
            markdown_description = row[3]
            link = row[1]
            print("--------------------------------")
            print(link)
            start_time = time.time()
            try:
                response = self.llm.as_structured_llm(Movies).chat(self._get_prompt(year, markdown_description))
            except Exception as e:
                print(f"Error: {e}")
                if isinstance(e, GoogleGenAIClientError) and e.code == 429:
                    print("LLM rate limit exceeded. Exiting...")
                    sys.exit(1)

                cursor.execute(
                    """
                    INSERT INTO llm_outputs (
                        post_id,
                        llm,
                        system_prompt,
                        error
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (row[0], self.model_name, self._get_system_prompt(year), str(e))
                )
                conn.commit()
                continue
            response_json = response.raw.model_dump_json()

            print(response_json)
            cursor.execute(
                """
                INSERT INTO llm_outputs (
                    post_id,
                    llm,
                    system_prompt,
                    output
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    row[0],
                    self.model_name,
                    self._get_system_prompt(year),
                    response_json
                )
            )
            conn.commit()
            print(f"Time taken: {time.time() - start_time} seconds")
            print("--------------------------------")
        conn.close()
    
    def _get_system_prompt(self, year):
        return f"""You are a cinema programming auditor. You need to collect screening information from the following text.
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
    
    def _get_prompt(self, year, text_content):
        messages = [
            ChatMessage(
                role="system",
                content=self._get_system_prompt(year)
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
    extract_screenings_from_markdown = ExtractScreeningsFromMarkdown()
    extract_screenings_from_markdown.run()