import os
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, ResultSet
import xml.etree.ElementTree as ET
import json
from datetime import datetime


class RSSCrawler:
    def __init__(self):
        self.url = "http://cinebancarios.blogspot.com/feeds/posts/default"
        self.dir = os.path.join("cinebancarios")
        self.current_page = 1
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

    def _get_rss(self, page=1):
        if os.path.exists(os.path.join(self.dir, f"rss_{page}.xml")):
            with open(os.path.join(self.dir, f"rss_{page}.xml"), "r") as f:
                return f.read()
        
        response = requests.get(self.url, params={"alt": "rss", "start-index": page})
        with open(os.path.join(self.dir, f"rss_{page}.xml"), "w") as f:
            f.write(response.text)
        return response.text

    def _parse_rss(self, rss):
        root = ET.fromstring(rss)
        return root

    def _get_posts(self):
        rss = self._get_rss()
        root = self._parse_rss(rss)
        return root.findall("channel/item")
    
    def _get_post_info(self, post):
        title = post.find("title").text
        link = post.find("link").text
        pubDate = post.find("pubDate").text
        
        # Try to get description if available
        description_elem = post.find("description")
        description = description_elem.text if description_elem is not None else ""
        
        # Try to get author if available
        author_elem = post.find("author")
        author = author_elem.text if author_elem is not None else ""
        
        # Create structured post data
        post_data = {
            "title": title,
            "link": link,
            "pubDate": pubDate,
            "description": description,
            "author": author,
            "scraped_at": datetime.now().isoformat()
        }
        
        return post_data
    
    def _generate_filename(self, page):
        """Generate a filename for the JSON file based on page number and timestamp"""
        return f"posts_page_{page:03d}.json"
    
    def _save_posts_to_json(self, posts_data, page):
        """Save posts data to a JSON file with filename"""
        filename = self._generate_filename(page)
        filepath = os.path.join(self.dir, filename)
        
        # Create structured data for the page
        page_data = {
            "page_number": page,
            "scraped_at": datetime.now().isoformat(),
            "total_posts": len(posts_data),
            "posts": posts_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(posts_data)} posts to {filename}")
        return filepath
    
    def run(self):
        while True:
            rss = self._get_rss(self.current_page)
            root = self._parse_rss(rss)
            posts = root.findall("channel/item")
            if not posts:
                break
            
            # Collect all posts data for this page
            posts_data = []
            for post in posts:
                post_data = self._get_post_info(post)
                posts_data.append(post_data)
                print(f"Processed: {post_data['title']}")
            
            # Save posts data to JSON file
            self._save_posts_to_json(posts_data, self.current_page)
            
            self.current_page += 1

if __name__ == "__main__":
    rss_crawler = RSSCrawler()
    rss_crawler.run()