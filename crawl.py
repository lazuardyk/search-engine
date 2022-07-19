from dotenv import load_dotenv
from crawler.crawl import Crawl

if __name__ == "__main__":
    load_dotenv()

    c = Crawl(start_urls=["https://www.indosport.com", "https://detik.com", "https://www.curiouscuisiniere.com"], max_threads="3", bfs_duration_sec="30", msb_duration_sec="30", msb_keyword="barcelona")
    c.run()