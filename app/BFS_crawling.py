import os
import bs4
import requests
import re
import pandas as pd
from collections import deque, Counter
import urllib.request
from urllib.parse import urljoin
import networkx as nx
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import time
import sys
import pymysql

# Using sys.setrecursionlimit() method 
sys.setrecursionlimit(100000000)

#conneting mysql database
db = pymysql.connect( host = 'localhost', user = 'root', passwd = '', db='crawler')
# prepare a cursor object using cursor() method
cursor = db.cursor()

# daftar url yang akan dicrawl
url_queue = deque([])

# daftar url yang sudah di crawl
visited_url = []

# titik awal: 1 situs
url_awal = input("URL Awal: ")

# keyword
hot_key = input("Keyword: ")


def tag_visible(element):
    """Function untuk merapihkan content text.
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, bs4.element.Comment):
        return False
    if re.match(r"[\n]+", str(element)):
        return False
    return True


def crawl(url):
    """Function untuk crawling page.
    """
    try:
        # kondisi berhenti
        time_now = time.time() - start_time
        time_now_int = int(time_now)
        if time_now_int >= 60:
            return

        # memasukan url kedalam visited_url
        visited_url.append(url)

        # crawl page
        print("page yang sedang di crawl:", url)
        page = requests.get(url)
        request = page.content
        soup = bs4.BeautifulSoup(request, 'html.parser')

        # extract title
        title = soup.title.string

        # check version html
        article_html5 = soup.find('article')
        if article_html5 is None:
            # extract text content from html4
            html5 = "no"
            texts = soup.find('body').findAll(text=True)
            visible_texts = filter(tag_visible, texts)
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
            visible_texts = filter(tag_visible, texts)
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
        cursor.execute(
            "SELECT base_url, COUNT(*) FROM page_information WHERE base_url = %s GROUP BY base_url",
            (url,)
        )
        results = cursor.fetchall()
        # gets the number of rows affected by the command executed
        row_count = cursor.rowcount
        if row_count == 0:
            # Create a new record
            sql = "INSERT INTO `page_information` (`base_url`, `html5`, `title`, `description`, `keywords`, `content_text`, `hot_url`, `model_crawl`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            # Execute the query
            cursor.execute(sql, (url, html5, title, description, keywords, complete_text, hot_link, "BFS crawling"))
            # commit to save our changes
            db.commit()
        else:
            # update database
            sql = "UPDATE page_information SET hot_url = %s WHERE base_url = %s"
            # Execute the query
            cursor.execute(sql, (hot_link, url))
            # commit to save our changes
            db.commit()

        # extract style
        for style in soup.findAll('style'):
            # Create a new record
            sql = "INSERT INTO `style_resource` (`base_url`, `style`) VALUES (%s, %s)"
            # Execute the query
            cursor.execute(sql, (url, style))
            # commit to save our changes
            db.commit()

        # extract script
        for script in soup.findAll('script'):
            # Create a new record
            sql = "INSERT INTO `script_resource` (`base_url`, `script`) VALUES (%s, %s)"
            # Execute the query
            cursor.execute(sql, (url, script))
            # commit to save our changes
            db.commit()

        # extract lists
        for lists in soup.findAll('li'):
            # Create a new record
            sql = "INSERT INTO `list` (`base_url`, `list`) VALUES (%s, %s)"
            # Execute the query
            cursor.execute(sql, (url, lists))
            # commit to save our changes
            db.commit()

        # extract forms
        for form in soup.findAll('form'):
            # Create a new record
            sql = "INSERT INTO `forms` (`base_url`, `form`) VALUES (%s, %s)"
            # Execute the query
            cursor.execute(sql, (url, form))
            # commit to save our changes
            db.commit()

        # extract tables
        for table in soup.findAll('table'):
            # Create a new record
            sql = "INSERT INTO `tables` (`base_url`, `tables`) VALUES (%s, %s)"
            # Execute the query
            cursor.execute(sql, (url, table))
            # commit to save our changes
            db.commit()

        # extract images
        for image in soup.findAll('img'):
            # Create a new record
            sql = "INSERT INTO `images` (`base_url`, `image`) VALUES (%s, %s)"
            # Execute the query
            cursor.execute(sql, (url, image))
            # commit to save our changes
            db.commit()

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
            list_g.append(branch)

            # Create a new record
            sql = "INSERT INTO `linking` (`crawl_id`, `url`, `outgoing_link`) VALUES (%s, %s, %s)"
            # Execute the query
            cursor.execute(sql, (1, url, complete_url))
            # commit to save our changes
            db.commit()

            # Check if the URL already exists in the url_queue
            for j in url_queue:
                if j == complete_url:
                    flag = 1
                    break

            # Check if the URL already exists in the visited_url
            for j in visited_url:
                if (j == complete_url):
                    flag = 1
                    break

            # If not found in queue
            if flag == 0:
                if (visited_url.count(complete_url)) == 0:
                    url_queue.append(complete_url)

    except (AttributeError, KeyError, requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
        title = "no-title"
        complete_text = "no-text"

    # crawl url selanjutnya
    if len(url_queue) == 0:
        return
    current = url_queue.popleft()
    
    crawl(current)


# time
start_time = time.time()

# graph
G = nx.DiGraph()
list_g = []

# crawl begin
crawl(url_awal)

print("Jumlah url yg sudah dicrawl:", len(visited_url))
print("Jumlan url dalam queue:", len(url_queue))
