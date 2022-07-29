from dotenv import load_dotenv
from src.crawling.crawl import Crawl
import os

if __name__ == "__main__":
    load_dotenv()
    start_urls = os.getenv("START_URLS").split()
    max_threads = os.getenv("MAX_THREADS")
    bfs_duration_sec = os.getenv("BFS_DURATION_SECONDS")
    msb_duration_sec = os.getenv("MSB_DURATION_SECONDS")
    msb_keyword = os.getenv("MSB_KEYWORD")

    c = Crawl(start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)
    c.run()