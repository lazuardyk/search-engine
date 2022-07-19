from crawler.database import Database
from crawler.modified_similarity_based import ModifiedSimilarityBased
from crawler.page_content import PageContent
from crawler.util import Util
from crawler.breadth_first_search import BreadthFirstSearch
import queue
import time
import bs4
from urllib.parse import urljoin
import psutil
import os

class Crawl:
    def __init__(self, start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword):
        self.start_urls = start_urls
        self.max_threads = int(max_threads)
        self.bfs_duration_sec = int(bfs_duration_sec)
        self.msb_duration_sec = int(msb_duration_sec)
        self.msb_keyword = msb_keyword
        self.db = Database()
        self.page_content = PageContent()
        self.util = Util()
        self.process = psutil.Process(os.getpid())
    
    def scrape_links_for_resume(self, urls):
        for url in urls:
            result = self.util.get_page(url)
            if result and result.status_code == 200:
                soup = bs4.BeautifulSoup(result.text, 'html.parser')
                links = soup.findAll("a", href=True)
                for i in links:
                    complete_url = urljoin(url, i["href"]).rstrip('/')
                    if self.util.is_valid_url(complete_url) and complete_url not in self.visited_urls:
                        self.url_queue.put(complete_url)
    
    def run(self):
        self.url_queue = queue.Queue()
        self.start_time = time.time()
        
        db_connection = self.db.connect()
        self.db.create_crawler_tables(db_connection)
        self.visited_urls = self.page_content.get_visited_urls(db_connection)
        self.page_count_start = self.db.count_rows(db_connection, "page_information")

        urls_string = ""
        if len(self.visited_urls) < 1:
            print("Starting the crawler from the start urls...")
            for url in self.start_urls:
                if self.util.is_valid_url(url):
                    self.url_queue.put(url)
                    urls_string += url + ", "
        else:
            print("Resuming the crawler from the last urls...")
            last_urls = self.visited_urls[-3:]
            for url in last_urls:
                urls_string += url + ", "
            self.scrape_links_for_resume(last_urls)
        urls_string = urls_string[0:len(urls_string) - 2]
        
        crawl_id = self.page_content.insert_crawling(db_connection, urls_string, "", 0, (self.bfs_duration_sec + self.msb_duration_sec))
        db_connection.close()

        print("Running breadth first search crawler...")
        bfs = BreadthFirstSearch(crawl_id, self.url_queue, self.visited_urls, self.bfs_duration_sec, self.max_threads)
        bfs.run()

        print("Running modified similarity based crawler...")
        msb = ModifiedSimilarityBased(crawl_id, bfs.url_queue, bfs.visited_urls, bfs.list_urls, self.msb_keyword, self.msb_duration_sec, self.max_threads)
        msb.run()

        db_connection = self.db.connect()
        self.page_count_end = self.db.count_rows(db_connection, "page_information")
        page_count = self.page_count_end - self.page_count_start
        self.page_content.update_crawling(db_connection, crawl_id, page_count)
        db_connection.close()