from typing import Any
from src.database.database import Database
from src.crawling.page_content import PageContent
from src.crawling.util import Util
from datetime import datetime
from urllib.parse import urljoin
import bs4
import threading
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures.thread
import queue
import time
import re


class BreadthFirstSearch:
    """
    Kelas yang digunakan untuk melakukan crawling dengan metode Breadth First Search.

    Args:
        crawl_id (int): ID crawling (table crawling di database)
        url_queue (queue.Queue): Kumpulan URL antrian
        visited_urls (list): Kumpulan URL yang sudah dikunjungi
        duration_sec (int): Durasi BFS crawler dalam detik
        max_threads (int): Maksimal threads yang akan digunakan
    """

    def __init__(
        self, crawl_id: int, url_queue: queue.Queue, visited_urls: list, duration_sec: int, max_threads: int
    ) -> None:
        self.crawl_id = crawl_id
        self.url_queue = url_queue
        self.visited_urls = visited_urls
        self.duration_sec = duration_sec
        self.max_threads = max_threads
        self.db = Database()
        self.page_content = PageContent()
        self.util = Util()
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.list_urls = []

    def run(self) -> None:
        """
        Fungsi utama yang berfungsi untuk menjalankan proses crawling BFS.
        """
        executor = ThreadPoolExecutor(max_workers=self.max_threads)

        futures = []
        while True:
            try:
                time_now = time.time() - self.start_time
                time_now_int = int(time_now)
                if time_now_int >= self.duration_sec:
                    print("Stopped because exceeded time limit...")
                    break
                target_url = self.url_queue.get(timeout=60)
                if target_url not in self.visited_urls:
                    self.visited_urls.append(target_url)
                    futures.append(executor.submit(self.scrape_page, target_url))
            except queue.Empty:
                if self.util.running_thread_count(futures) > 0:
                    continue
                else:
                    print("Stopped because empty queue...")
                    break
            except KeyboardInterrupt:
                print("Stopped because keyboard interrupt...")
                break
            except Exception as e:
                print(e)
                continue

        executor._threads.clear()
        concurrent.futures.thread._threads_queues.clear()

    def scrape_page(self, url: str) -> None:
        """
        Fungsi untuk menyimpan konten yang ada pada suatu halaman ke database.

        Args:
            url (str): URL halaman yang ingin discrape
        """
        try:
            page_start_time = time.time()
            response = self.util.get_page(url)
            if response and response.status_code == 200:
                db_connection = self.db.connect()
                self.lock.acquire()
                now = datetime.now()
                print(url, "| BFS |", now.strftime("%d/%m/%Y %H:%M:%S"))
                self.lock.release()
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                title = soup.title.string
                article_html5 = soup.find("article")
                if article_html5 is None:
                    # extract text content from html4
                    html5 = 0
                    texts = soup.find("body").findAll(text=True)
                    visible_texts = filter(self.tag_visible, texts)
                    text = " ".join(t.strip() for t in visible_texts)
                    text = text.lstrip().rstrip()
                    text = text.split(",")
                    clean_text = ""
                    for sen in text:
                        if sen:
                            sen = sen.rstrip().lstrip()
                            clean_text += sen + ","
                    complete_text = clean_text
                else:
                    # extract text content from html5
                    html5 = 1
                    texts = article_html5.findAll(text=True)
                    visible_texts = filter(self.tag_visible, texts)
                    text = " ".join(t.strip() for t in visible_texts)
                    text = text.lstrip().rstrip()
                    text = text.split(",")
                    clean_text = ""
                    for sen in text:
                        if sen:
                            sen = sen.rstrip().lstrip()
                            clean_text += sen + ","
                    complete_text = clean_text

                # get meta description
                description = soup.find("meta", attrs={"name": "description"})
                if description is None:
                    description = "-"
                else:
                    description = description.get("content")

                # get meta keywords
                keywords = soup.find("meta", attrs={"name": "keywords"})
                if keywords is None:
                    keywords = "-"
                else:
                    keywords = keywords.get("content")

                # isHotURL
                hot_link = 0

                # check if the page information already exist
                if self.db.check_value_in_table(db_connection, "page_information", "url", url):
                    self.db.close_connection(db_connection)
                    return

                # extract style
                for style in soup.findAll("style"):
                    self.page_content.insert_page_style(db_connection, url, style)

                # extract script
                for script in soup.findAll("script"):
                    self.page_content.insert_page_script(db_connection, url, script)

                # extract lists
                for lists in soup.findAll("li"):
                    self.page_content.insert_page_list(db_connection, url, lists)

                # extract forms
                for form in soup.findAll("form"):
                    self.page_content.insert_page_form(db_connection, url, form)

                # extract tables
                for table in soup.findAll("table"):
                    self.page_content.insert_page_table(db_connection, url, table)

                # extract images
                for image in soup.findAll("img"):
                    self.page_content.insert_page_image(db_connection, url, image)

                # extract outgoing link
                links = soup.findAll("a", href=True)
                for i in links:
                    # Complete relative URLs and strip trailing slash
                    complete_url = urljoin(url, i["href"]).rstrip("/")

                    self.list_urls.append(complete_url)  # For  MSB
                    self.page_content.insert_page_linking(db_connection, self.crawl_id, url, complete_url)

                    self.lock.acquire()
                    if self.util.is_valid_url(complete_url) and complete_url not in self.visited_urls:
                        self.url_queue.put(complete_url)
                    self.lock.release()

                page_duration_crawl = time.time() - page_start_time
                self.page_content.insert_page_information(
                    db_connection,
                    url,
                    self.crawl_id,
                    html5,
                    title,
                    description,
                    keywords,
                    complete_text,
                    hot_link,
                    "BFS crawling",
                    int(page_duration_crawl),
                )
                self.db.close_connection(db_connection)
                return
            return
        except Exception as e:
            print(e, "~ Error in thread")
            return

    def tag_visible(self, element: Any) -> bool:
        """
        Fungsi untuk merapihkan konten teks.

        Args:
            element (Any): Elemen HTML
        """
        if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
            return False
        if isinstance(element, bs4.element.Comment):
            return False
        if re.match(r"[\n]+", str(element)):
            return False
        return True
