from src.database.database import Database
from src.crawling.methods.modified_similarity_based import ModifiedSimilarityBased
from src.crawling.page_content import PageContent
from src.crawling.util import Util
from src.crawling.methods.breadth_first_search import BreadthFirstSearch
import queue
import time
import bs4
from urllib.parse import urljoin
import psutil
import os
import warnings


class Crawl:
    """
    Kelas utama untuk melakukan proses crawling.

    Args:
        start_urls (list): Kumpulan URL awal yang ingin dicrawl
        max_threads (str): Maksimal threads yang akan digunakan
        bfs_duration_sec (str): Durasi untuk crawler BFS dalam detik
        msb_duration_sec (str): Durasi untuk crawler MSB dalam detik
        msb_keyword (str): Keyword yang digunakan untuk crawler MSB
    """

    def __init__(
        self, start_urls: list, max_threads: str, bfs_duration_sec: str, msb_duration_sec: str, msb_keyword: str
    ) -> None:
        self.start_urls = start_urls
        self.max_threads = int(max_threads)
        self.bfs_duration_sec = int(bfs_duration_sec)
        self.msb_duration_sec = int(msb_duration_sec)
        self.msb_keyword = msb_keyword
        self.db = Database()
        self.page_content = PageContent()
        self.util = Util()
        self.process = psutil.Process(os.getpid())
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    def scrape_links_for_resume(self, urls: list) -> None:
        """
        Fungsi untuk mengambil semua link pada halaman yang dilakukan pada saat resume proses crawling.

        Args:
            urls (list): Kumpulan URL halaman yang akan diekstrak linknya
        """
        for url in urls:
            result = self.util.get_page(url)
            if result and result.status_code == 200:
                soup = bs4.BeautifulSoup(result.text, "html.parser")
                links = soup.findAll("a", href=True)
                for i in links:
                    complete_url = urljoin(url, i["href"]).rstrip("/")
                    if self.util.is_valid_url(complete_url) and complete_url not in self.visited_urls:
                        self.url_queue.put(complete_url)

    def run(self) -> None:
        """
        Fungsi utama yang berfungsi untuk menjalankan proses crawling.
        """
        self.url_queue = queue.Queue()
        self.start_time = time.time()

        db_connection = self.db.connect()
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
        urls_string = urls_string[0 : len(urls_string) - 2]

        crawl_id = self.page_content.insert_crawling(
            db_connection, urls_string, "", 0, (self.bfs_duration_sec + self.msb_duration_sec)
        )
        db_connection.close()

        print("Running breadth first search crawler...")
        bfs = BreadthFirstSearch(crawl_id, self.url_queue, self.visited_urls, self.bfs_duration_sec, self.max_threads)
        bfs.run()
        print("Finished breadth first search crawler...")

        # Disable Modified Similarity Based Crawler

        print(len(bfs.list_urls))
        print("Running modified similarity based crawler...")
        msb = ModifiedSimilarityBased(
            crawl_id,
            bfs.url_queue,
            bfs.visited_urls,
            bfs.list_urls,
            self.msb_keyword,
            self.msb_duration_sec,
            self.max_threads,
        )
        msb.run()
        print("Finished modified similarity based crawler...")

        db_connection = self.db.connect()
        self.page_count_end = self.db.count_rows(db_connection, "page_information")
        page_count = self.page_count_end - self.page_count_start
        self.page_content.update_crawling(db_connection, crawl_id, page_count)
        db_connection.close()
