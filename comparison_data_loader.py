import json
from pathlib import Path
from typing import Iterable, List

from llama_index.core import Document


def load_and_clean_movies_docs(json_dir: Path | str, fields_to_remove: Iterable[str]) -> List[Document]:
    json_dir = Path(json_dir)
    text_list: List[str] = []

    for path in json_dir.iterdir():
        data = json.loads(path.read_text(encoding="utf-8"))
        movies = data.get("output", {}).get("movies", [])
        if isinstance(movies, list):
            for movie in movies:
                if isinstance(movie, dict):
                    for field in fields_to_remove:
                        movie.pop(field, None)
        text_list.append(json.dumps(data, ensure_ascii=False))

    return [
        Document(
            text=text,
        ) for text in text_list
    ]
