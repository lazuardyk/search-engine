from dotenv import load_dotenv
from source.crawling.crawl import Crawl
from source.database.database import Database
import os

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    start_urls = os.getenv("CRAWLER_START_URLS").split()
    max_threads = os.getenv("CRAWLER_MAX_THREADS")
    crawler_duration_sec = os.getenv("CRAWLER_DURATION_SECONDS")
    try:
        msb_keyword = os.getenv("CRAWLER_KEYWORD")
    except:
        msb_keyword = ""

    if msb_keyword != "":
        bfs_duration_sec = int(crawler_duration_sec) // 2
        msb_duration_sec = int(crawler_duration_sec) // 2
    else:
        bfs_duration_sec = int(crawler_duration_sec)
        msb_duration_sec = 0

    c = Crawl(start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)
    c.run()
