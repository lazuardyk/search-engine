from flask import Blueprint
from src.page_ranking.page_rank import PageRank

bp_page_ranking = Blueprint("page_ranking", __name__)


@bp_page_ranking.route("/page_rank")
def get_page_rank_ranks():
    try:
        page_rank = PageRank()
        data = page_rank.get_all_pagerank()
        return {
            "ok": True,
            "message": "Sukses",
            "data": data,
        }
    except Exception as e:
        return {
            "ok": False,
            "message": e,
            "data": [],
        }
