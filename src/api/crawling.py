from flask import Blueprint, request
from src.crawling.page_content import PageContent
import json

bp_crawling = Blueprint("crawling", __name__)


@bp_crawling.route("/pages")
def get_crawled_pages():
    try:
        start_index = request.args.get("start", default="", type=str)
        end_index = request.args.get("end", default="", type=str)

        page_content = PageContent()
        if start_index != "" and end_index != "":
            data = page_content.get_crawled_pages(int(start_index), int(end_index))
        else:
            data = page_content.get_crawled_pages()

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
            "data": [],
        }
