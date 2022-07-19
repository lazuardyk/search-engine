from concurrent.futures import thread
from crawler.database import Database
from crawler.page_content import PageContent
from crawler.util import Util
from collections import deque
from queue import Queue
import time
import requests
import bs4
import re
from urllib.parse import urljoin
import threading

class Crawl:
    def __init__(self, start_url, keyword, duration, core_total):
        self.start_url = start_url
        self.keyword = keyword
        self.duration = int(duration)
        self.core_total = int(core_total)
        self.db = Database()
        self.page_content = PageContent()
        self.util = Util()
    
    def run(self):
        db_connection = self.db.connect()
        self.db.create_crawler_tables(db_connection)
        db_connection.close()

        self.url_queue = Queue()
        self.url_queue.put(self.start_url)
        self.visited_url = set()
        self.start_time = time.time()
        self.list_g = []
        self.lock = threading.Lock()

        crawler_threads = []

        for i in range(int(self.core_total)):
            db_connection = self.db.connect()
            t = threading.Thread(target=self.bfs_crawling, args=(db_connection, ))
            t.start()
            crawler_threads.append(t)
            time.sleep(10)
        
        for crawler in crawler_threads:
            crawler.join()
        
        print("bfs kelar")
        self.url_queue = self.reorder_queue(self.url_queue)
        self.hot_queue = Queue()
        print("reorder kelar")
        self.start_time_2 = time.time()
        crawler2_threads = []

        for i in range(int(self.core_total)):
            db_connection = self.db.connect()
            t = threading.Thread(target=self.modified_crawling, args=(db_connection, ))
            t.start()
            crawler2_threads.append(t)
            time.sleep(10)
        
        for crawler in crawler2_threads:
            crawler.join()
        
        print("modified kelar")
        
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
    
    def bfs_crawling(self, db_connection):
        while True:
            try:
                if self.url_queue.qsize() < 1:
                    break
                self.lock.acquire()
                url = self.url_queue.get()
                self.lock.release()
                time_now = time.time() - self.start_time
                time_now_int = int(time_now)
                if time_now_int >= self.duration//2:
                    self.db.close_connection(db_connection)
                    break
                visited = False
                if url in self.visited_url:
                    visited = True

                if visited:
                    # if self.url_queue.qsize() < 1:
                    #     self.db.close_connection(db_connection)
                    #     break
                    continue

                print("page yang sedang di crawl:", url, threading.current_thread())
                self.lock.acquire()
                self.visited_url.add(url)
                self.lock.release()

                page = requests.get(url)
                request = page.content
                soup = bs4.BeautifulSoup(request, 'html.parser')
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
                    flag = 0

                    # Complete relative URLs and strip trailing slash
                    complete_url = urljoin(url, i["href"]).rstrip('/')

                    # create graph
                    # G.add_edges_from([(url, complete_url)])

                    # create list graph
                    branch = []
                    # remove https://
                    new_url = url.replace('https://', '')
                    new_url = new_url.replace('http://', '')
                    new_complete = complete_url.replace('https://', '')
                    new_complete = new_complete.replace('http://', '')
                    branch.append(new_url)
                    branch.append(new_complete)
                    self.list_g.append(complete_url)

                    # Create a new record
                    self.page_content.insert_page_linking(db_connection, 1, url, complete_url)

                    # Check if the URL already exists in the visited_url
                    if complete_url in self.visited_url:
                        flag = 1

                    # If not found in queue
                    if flag == 0:
                        self.lock.acquire()
                        self.url_queue.put(complete_url)
                        self.lock.release()
            except (AttributeError, KeyError, requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
                title = "no-title"
                complete_text = "no-text"
            
            # crawl url selanjutnya
            # if self.url_queue.qsize() < 1:
            #     self.db.close_connection(db_connection)
            #     break
            continue

        return
    
    def reorder_queue(self, q):
        """Function untuk reorder queue"""
        value_backlink = []
        for u in list(q.queue):
            # menentukan nilai backlink_count
            backlink_count = self.list_g.count(u)
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
            self.lock.acquire()
            q.put(i[0])
            self.lock.release()
        return q
    
    def modified_crawling(self, db_connection):
        while True:
            try:
                if self.hot_queue.qsize() > 0:
                    self.lock.acquire()
                    url = self.hot_queue.get()
                    self.lock.release()
                elif self.url_queue.qsize() > 0:
                    self.lock.acquire()
                    url = self.url_queue.get()
                    self.lock.release()
                else:
                    break
                # kondisi berhenti biar ga running all the time
                time_now = time.time() - self.start_time_2
                time_now_int = int(time_now)
                if time_now_int >= self.duration:
                    self.db.close_connection(db_connection)
                    break

                visited = False
                if url in self.visited_url:
                    visited = True

                if visited:
                    # print("visited")
                    # if self.url_queue.qsize() < 1:
                    #     self.db.close_connection(db_connection)
                    #     break
                    continue


                # memasukan url kedalam visited_url
                self.lock.acquire()
                self.visited_url.add(url)
                self.lock.release()

                # crawl page
                print("page yang sedang di crawl (modified):", url, threading.current_thread())
                page = requests.get(url)
                request = page.content
                soup = bs4.BeautifulSoup(request, 'html.parser')
                
                # extract title
                title = soup.title.string
                # print("judul:", title)

                # check version html
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

                # check hot_url
                hot_url = False
                hot_link = "no"
                if (self.util.count_keyword_in_text(complete_text, self.keyword) >= 10) or (self.util.count_keyword_in_text(title, self.keyword) >= 1):
                    hot_url = True
                    hot_link = "yes"

                # Create a new record
                self.page_content.insert_page_information(db_connection, url, html5, title, description, keywords, complete_text, hot_link, "modified similarity-based crawling")

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
                    flag = 0

                    # Complete relative URLs and strip trailing slash
                    complete_url = urljoin(url, i["href"]).rstrip('/')

                    # create list graph
                    branch = []
                    # remove https://
                    new_url = url.replace('https://', '')
                    new_url = new_url.replace('http://', '')
                    new_complete = complete_url.replace('https://', '')
                    new_complete = new_complete.replace('http://', '')
                    branch.append(new_url)
                    branch.append(new_complete)
                    self.list_g.append(complete_url)

                    # Create a new record
                    self.page_content.insert_page_linking(db_connection, 1, url, complete_url)

                    # Check if the URL already exists in the url_queue
                    # for j in self.url_queue:
                    #     if (j == complete_url):
                    #         flag = 1
                    #         break

                    # # Check if the URL already exists in the hot_queue
                    # for j in self.hot_queue:
                    #     if (j == complete_url):
                    #         flag = 1
                    #         break

                    # Check if the URL already exists in the visited_url
                    # for j in self.visited_url:
                    #     if (j == complete_url):
                    #         flag = 1
                    #         break

                    if complete_url in self.visited_url:
                        flag = 1

                    # If not found in queue
                    if flag == 0:
                        # kondisi yang dimasukan ke hot_queue dan url_queue
                        if (hot_url == True) or ((complete_url.count("klub-bola-barcelona") >= 1)):
                            self.lock.acquire()
                            self.hot_queue.put(complete_url)
                            self.lock.release()
                        else:
                            self.lock.acquire()
                            self.url_queue.put(complete_url)
                            self.lock.release()

                self.hot_queue = self.reorder_queue(self.hot_queue)
                self.url_queue = self.reorder_queue(self.url_queue)

            except Exception as e:
                print(e)
                title = "no-title"
                complete_text = "no-text"
        
        return
        # crawl url selanjutnya
        # if len(self.hot_queue) > 0:
        #     current = self.hot_queue.popleft()
        # else:
        #     current = self.url_queue.popleft()
        # self.modified_crawling(current)