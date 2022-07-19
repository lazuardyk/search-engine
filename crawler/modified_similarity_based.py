from matplotlib.pyplot import hot
from crawler.database import Database
from crawler.page_content import PageContent
from crawler.util import Util
from datetime import datetime
from urllib.parse import urljoin
import bs4
import threading
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures.thread
import queue
import time
import re

class ModifiedSimilarityBased:
    def __init__(self, crawl_id, url_queue, visited_urls, list_urls, keyword, duration_sec, max_threads):
        self.crawl_id = crawl_id
        self.url_queue = self.reorder_queue(url_queue)
        self.visited_urls = visited_urls
        self.keyword = keyword
        self.duration_sec = duration_sec
        self.max_threads = max_threads
        self.db = Database()
        self.page_content = PageContent()
        self.util = Util()
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.list_urls = list_urls
        self.hot_queue = queue.Queue()
    
    def run(self):
        executor = ThreadPoolExecutor(max_workers=self.max_threads)

        while True:
            try:
                time_now = time.time() - self.start_time
                time_now_int = int(time_now)
                if time_now_int >= self.duration_sec:
                    print(time_now_int)
                    break
                if self.hot_queue.qsize() > 0:
                    target_url = self.hot_queue.get()
                else:
                    target_url = self.url_queue.get()
                if target_url not in self.visited_urls:
                    self.visited_urls.append(target_url)
                    executor.submit(self.scrape_page, target_url)
                
                self.hot_queue = self.reorder_queue(self.hot_queue)
                self.url_queue = self.reorder_queue(self.url_queue)
            except queue.Empty:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
                continue
        
        executor._threads.clear()
        concurrent.futures.thread._threads_queues.clear()

    def scrape_page(self, url):
        response = self.util.get_page(url)
        if response and response.status_code == 200:
            db_connection = self.db.connect()
            self.lock.acquire()
            now = datetime.now()
            print(url, "| MSB |", now.strftime("%d/%m/%Y %H:%M:%S"))
            self.lock.release()
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
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

            # check hot_url
            hot_link = "no"
            if (self.util.count_keyword_in_text(complete_text, self.keyword) >= 10) or (self.util.count_keyword_in_text(title, self.keyword) >= 1):
                hot_link = "yes"

            # check if the page information already exist
            if not self.db.check_value_in_table(db_connection, "page_information", "url", url):
                self.page_content.insert_page_information(db_connection, url, self.crawl_id, html5, title, description, keywords, complete_text, hot_link, "MSB crawling")
            else:
                self.db.close_connection(db_connection)
                return

            # extract style
            for style in soup.findAll('style'):
                self.page_content.insert_page_style(db_connection, url, style)

            # extract script
            for script in soup.findAll('script'):
                self.page_content.insert_page_script(db_connection, url, script)

            # extract lists
            for lists in soup.findAll('li'):
                self.page_content.insert_page_list(db_connection, url, lists)

            # extract forms
            for form in soup.findAll('form'):
                self.page_content.insert_page_form(db_connection, url, form)

            # extract tables
            for table in soup.findAll('table'):
                self.page_content.insert_page_table(db_connection, url, table)

            # extract images
            for image in soup.findAll('img'):
                self.page_content.insert_page_image(db_connection, url, image)

            # extract outgoing link
            links = soup.findAll("a", href=True)
            for i in links:
                # Complete relative URLs and strip trailing slash
                complete_url = urljoin(url, i["href"]).rstrip('/')

                self.list_urls.append(complete_url)
                self.page_content.insert_page_linking(db_connection, self.crawl_id, url, complete_url)

                self.lock.acquire()
                if self.util.is_valid_url(complete_url) and complete_url not in self.visited_urls:
                    if hot_link == "yes" or self.keyword in url:
                        self.hot_queue.put(complete_url)
                    else:
                        self.url_queue.put(complete_url)
                self.lock.release()

            self.db.close_connection(db_connection)
    
    def tag_visible(self, element):
        """Function untuk merapihkan content text."""
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, bs4.element.Comment):
            return False
        if re.match(r"[\n]+", str(element)):
            return False
        return True
    
    def reorder_queue(self, q):
        value_backlink = []
        for u in list(q.queue):
            # menentukan nilai backlink_count
            backlink_count = self.list_urls.count(u)
            # print(backlink_count)
            # memasukan backlink_count ke array value_backlink
            value_backlink.append(backlink_count)
            
        # membuat dictionary backlink untuk proses sorting
        backlink_dictionary = dict(zip(q.queue, value_backlink))
        
        # sorting backlink_dictionary
        sort_orders = sorted(backlink_dictionary.items(),
                            key=lambda x: x[1], reverse=True)
        # mengkosongkan queue
        with q.mutex:
            q.queue.clear()

        # membuat queue yang sudah di sort
        for i in sort_orders:
            q.put(i[0])

        return q


    