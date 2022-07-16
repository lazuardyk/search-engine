from app.database import Database
from app.page_content import PageContent
from app.util import Util
import queue
import time
import requests
from datetime import datetime
import bs4
import re
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pynput import keyboard
import psutil
import os

class Crawl:
    def __init__(self, start_urls, max_threads):
        self.start_urls = start_urls
        self.max_threads = int(max_threads)
        self.db = Database()
        self.page_content = PageContent()
        self.util = Util()
        self.process = psutil.Process(os.getpid())
        self.status = "running"
    
    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)

    def get_page(self, url):
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res
        except Exception as e:
            print(e)
            return
    
    def on_press(self, key):
        if key == keyboard.Key.esc:
            print("Crawler killed.")
            self.process.kill()
        try:
            k = key.char
        except:
            k = key.name 
        if k in ['p', 'r']: 
            if k == "p":
                self.status = "paused"
                print("Crawler paused.")
            else:
                self.status = "running"
                print("Crawler resumed.")
    
    def scrape_page(self, url, future):
        result = future.result()
        if result and result.status_code == 200:
            db_connection = self.db.connect()
            self.lock.acquire()
            now = datetime.now()
            print(url, now.strftime("%d/%m/%Y %H:%M:%S"))
            self.lock.release()
            soup = bs4.BeautifulSoup(result.text, 'html.parser')
            title = soup.title.string
            article_html5 = soup.find('article')
            if article_html5 is None:
                # extract text content from html4
                html5 = "no"
                texts = soup.find('body').findAll(text=True)
                visible_texts = filter(self.tag_visible, texts)
                text = u" ".join(t.strip() for t in visible_texts)
                text = text.lstrip().rstrip()
                text = text.split(',')
                clean_text = ''
                for sen in text:
                    if sen:
                        sen = sen.rstrip().lstrip()
                        clean_text += sen+','
                complete_text = clean_text
                # print(complete_text)
            else:
                # extract text content from html5
                html5 = "yes"
                texts = article_html5.findAll(text=True)
                visible_texts = filter(self.tag_visible, texts)
                text = u" ".join(t.strip() for t in visible_texts)
                text = text.lstrip().rstrip()
                text = text.split(',')
                clean_text = ''
                for sen in text:
                    if sen:
                        sen = sen.rstrip().lstrip()
                        clean_text += sen+','
                complete_text = clean_text
                # print(complete_text)

            # get meta description
            description = soup.find("meta",attrs={"name":"description"})
            if description is None:
                description = "-"
            else:
                description = description.get("content")

            # get meta keywords
            keywords = soup.find("meta",attrs={"name":"keywords"})
            if keywords is None:
                keywords = "-"
            else:
                keywords = keywords.get("content")

            # isHotURL
            hot_link = "no"

            # check table if exist at crawldb  
            if not self.db.check_value_in_table(db_connection, "page_information", "url", url):
                # Create a new record
                self.page_content.insert_page_information(db_connection, url, html5, title, description, keywords, complete_text, hot_link, "BFS crawling")
            else:
                # update database
                self.page_content.set_hot_url(db_connection, url, hot_link)

            # extract style
            for style in soup.findAll('style'):
                # Create a new record
                self.page_content.insert_page_style(db_connection, url, style)

            # extract script
            for script in soup.findAll('script'):
                # Create a new record
                self.page_content.insert_page_script(db_connection, url, script)

            # extract lists
            for lists in soup.findAll('li'):
                # Create a new record
                self.page_content.insert_page_list(db_connection, url, lists)

            # extract forms
            for form in soup.findAll('form'):
                # Create a new record
                self.page_content.insert_page_form(db_connection, url, form)

            # extract tables
            for table in soup.findAll('table'):
                # Create a new record
                self.page_content.insert_page_table(db_connection, url, table)

            # extract images
            for image in soup.findAll('img'):
                # Create a new record
                self.page_content.insert_page_image(db_connection, url, image)

            # extract outgoing link
            links = soup.findAll("a", href=True)

            # memasukan outgoing link kedalam queue
            for i in links:
                # Complete relative URLs and strip trailing slash
                complete_url = urljoin(url, i["href"]).rstrip('/')

                # Create a new record
                self.page_content.insert_page_linking(db_connection, 1, url, complete_url)

                self.lock.acquire()
                if self.is_valid_url(complete_url) and complete_url not in self.visited_url:
                    self.url_queue.put(complete_url)
                self.lock.release()

            self.db.close_connection(db_connection)
    
    def run(self):
        db_connection = self.db.connect()
        self.db.create_crawler_tables(db_connection)
        db_connection.close()

        self.url_queue = queue.Queue()
        self.visited_url = []
        self.start_time = time.time()
        self.lock = threading.Lock()
        self.event_stop = threading.Event()

        for url in self.start_urls:
            if self.is_valid_url(url):
                self.url_queue.put(url)
        
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        executor = ThreadPoolExecutor(max_workers=self.max_threads)

        while True:
            try:
                if self.status == "paused":
                    time.sleep(1)
                    continue
                target_url = self.url_queue.get(timeout=60)
                if target_url not in self.visited_url:
                    self.visited_url.append(target_url)
                    # with ThreadPoolExecutor(self.max_threads) as executor:
                    future = executor.submit(self.get_page, target_url)
                    future.add_done_callback(partial(self.scrape_page, target_url))
            except queue.Empty:
                return
            except Exception as e:
                print(e)
                continue

        # crawler_threads = []

        # for i in range(int(self.core_total)):
        #     db_connection = self.db.connect()
        #     t = threading.Thread(target=self.bfs_crawling, args=(db_connection, ))
        #     t.start()
        #     crawler_threads.append(t)
        #     time.sleep(10)
        
        # for crawler in crawler_threads:
        #     crawler.join()
        
        # print("bfs kelar")
        # self.url_queue = self.reorder_queue(self.url_queue)
        # self.hot_queue = Queue()
        # print("reorder kelar")
        # self.start_time_2 = time.time()
        # crawler2_threads = []

        # for i in range(int(self.core_total)):
        #     db_connection = self.db.connect()
        #     t = threading.Thread(target=self.modified_crawling, args=(db_connection, ))
        #     t.start()
        #     crawler2_threads.append(t)
        #     time.sleep(10)
        
        # for crawler in crawler2_threads:
        #     crawler.join()
        
        # print("modified kelar")
        
        time_now = time.time() - self.start_time
        time_now_int = int(time_now)
        db_connection = self.db.connect()
        self.page_content.insert_crawling(db_connection, self.start_url, self.keyword, len(self.visited_url), time_now_int)
        db_connection.close()
        # self.bfs_crawling(self.start_url)

        # self.url_queue = self.reorder_queue(self.url_queue)
        # self.hot_queue = deque([])
        # self.start_time_2 = time.time()
        # self.modified_crawling(self.url_queue.popleft())
        # time_now = time.time() - self.start_time
        # time_now_int = int(time_now)
        # self.page_content.insert_crawling(self.start_url, self.keyword, len(self.visited_url), time_now_int)
    
    def tag_visible(self, element):
        """Function untuk merapihkan content text."""
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, bs4.element.Comment):
            return False
        if re.match(r"[\n]+", str(element)):
            return False
        return True