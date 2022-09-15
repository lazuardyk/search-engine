from flask import Blueprint, request
from src.crawling.page_content import PageContent
from src.crawling.crawl import Crawl
import json

bp_crawling = Blueprint("crawling", __name__)


@bp_crawling.route("/crawl")
def run_crawling():
    try:
        crawler_duration_sec = request.args.get("duration", default="", type=str)
        start_urls = request.args.get("start_url", default="", type=str)
        max_threads = request.args.get("threads", default="", type=str)
        msb_keyword = request.args.get("keyword", default="", type=str)

        if msb_keyword != "":
            bfs_duration_sec = int(crawler_duration_sec) // 2
            msb_duration_sec = int(crawler_duration_sec) // 2
        else:
            bfs_duration_sec = int(crawler_duration_sec)
            msb_duration_sec = 0

        c = Crawl(start_urls, max_threads, bfs_duration_sec, msb_duration_sec, msb_keyword)
        page_count = c.run()
        data = {"total_pages": page_count}
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


@bp_crawling.route("/pages")
def get_crawled_pages():
    try:
        start_index = request.args.get("start", default="", type=str)
        end_index = request.args.get("length", default="", type=str)

        page_content = PageContent()
        if start_index != "" and end_index != "":
            data = page_content.get_crawled_pages_api(int(start_index), int(end_index))
        else:
            data = page_content.get_crawled_pages_api()

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
        page_content = PageContent()

        id_crawling = page_content.start_insert_api(start_urls, keyword, duration_crawl)

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
        page_content = PageContent()

        page_content.insert_page_api(
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
