from flask import Blueprint, request
from src.crawling.crawl import Crawl
from src.crawling.crawl import CrawlUtils
import json
import os
from concurrent.futures import ThreadPoolExecutor

bp_crawling = Blueprint("crawling", __name__)


@bp_crawling.route("/crawl")
def run_crawling():
    try:
        crawler_duration_sec = request.args.get("duration", default="", type=str)
        start_urls = os.getenv("CRAWLER_START_URLS").split()
        max_threads = os.getenv("CRAWLER_MAX_THREADS")
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

        executor = ThreadPoolExecutor(max_workers=1)
        c = Crawl(start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)
        executor.submit(c.run)

        response = {
            "ok": True,
            "message": "Sukses",
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500


@bp_crawling.route("/pages")
def get_crawled_pages():
    try:
        start_index = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        crawl_utils = CrawlUtils()
        if start_index != "" and length != "":
            data = crawl_utils.get_crawled_pages_api(int(start_index), int(length))
        else:
            data = crawl_utils.get_crawled_pages_api()

        response = {
            "ok": True,
            "message": "Sukses",
            "data": data,
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500


@bp_crawling.route("/page_information")
def get_page_information():
    try:
        id_page = request.args.get("id", default="", type=str)

        crawl_utils = CrawlUtils()
        if id_page != "":
            data = crawl_utils.get_page_information_api(int(id_page))
        else:
            data = []

        response = {
            "ok": True,
            "message": "Sukses",
            "data": data,
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200

    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500


@bp_crawling.route("/start_insert", methods=["POST"])
def start_insert_pages():
    try:
        start_urls = request.json["start_urls"]
        keyword = request.json["keyword"]
        duration_crawl = request.json["duration_crawl"]
        crawl_utils = CrawlUtils()

        id_crawling = crawl_utils.start_insert_api(start_urls, keyword, duration_crawl)

        response = {
            "ok": True,
            "message": "Sukses",
            "data": {"id_crawling": id_crawling},
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200
    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500


@bp_crawling.route("/insert_page", methods=["POST"])
def insert_page():
    try:
        page_information = request.json["page_information"]
        page_forms = request.json["page_forms"]
        page_images = request.json["page_images"]
        page_linking = request.json["page_linking"]
        page_list = request.json["page_list"]
        page_scripts = request.json["page_scripts"]
        page_styles = request.json["page_styles"]
        page_tables = request.json["page_tables"]
        crawl_utils = CrawlUtils()

        crawl_utils.insert_page_api(
            page_information, page_forms, page_images, page_linking, page_list, page_scripts, page_styles, page_tables
        )

        response = {
            "ok": True,
            "message": "Sukses",
        }
        json_obj = json.dumps(response, indent=4, default=str)
        return json.loads(json_obj), 200
    except Exception as e:
        return {
            "ok": False,
            "message": e,
        }, 500
