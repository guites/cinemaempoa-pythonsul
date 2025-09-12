import json
import os
from datetime import datetime


class JsonSorter:
    def __init__(self, directory):
        self.directory = directory
        self.slugs = set()
        self.posts = []

    def sort_json(self):
        for file in os.listdir(self.directory):
            if not file.endswith(".json"):
                continue
            if not file.startswith("posts_page_"):
                continue
            file_data = None
            with open(os.path.join(self.directory, file), 'r') as f:
                try:
                    file_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error loading {file}")
                    continue
            if file_data is None:
                continue
            for post in file_data["posts"]:
                post_slug = post["link"].split(".com/")[-1].replace("/", "-")
                if post_slug in self.slugs:
                    continue
                self.slugs.add(post_slug)
                parsedPubDate = datetime.strptime(post["pubDate"], "%a, %d %b %Y %H:%M:%S %z")
                post["pubDate"] = parsedPubDate.isoformat()
                self.posts.append(post)

        self.posts.sort(key=lambda x: x["pubDate"], reverse=True)
        with open(os.path.join(self.directory, "sorted.json"), 'w') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)

        return self.posts

if __name__ == "__main__":
    json_sorter = JsonSorter("cinebancarios/")
    json_sorter.sort_json()