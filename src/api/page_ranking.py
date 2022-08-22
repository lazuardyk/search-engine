from flask import Blueprint
from src.page_ranking.page_rank import PageRank
import json

bp_page_ranking = Blueprint("page_ranking", __name__)


@bp_page_ranking.route("/page_rank")
def get_page_rank_ranks():
    try:
        page_rank = PageRank()
        data = page_rank.get_all_pagerank()
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
