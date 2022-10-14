from flask import Blueprint, request
from src.overall_ranking.similarity import Similarity
import json

bp_overall_ranking = Blueprint(
    "overall_ranking",
    __name__,
)


@bp_overall_ranking.route("/similarity")
def get_similarity_ranks():
    try:
        keyword = request.args.get("keyword", default="", type=str)
        sort = request.args.get("sort", default="similarity", type=str)
        start = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        similarity = Similarity()
        if keyword == "":
            response = {
                "ok": False,
                "message": "Keyword tidak ada. Masukkan keyword pada url seperti '?keyword=barcelona'",
            }
        else:
            if start != "" and length != "":
                data = similarity.get_all_similarity_for_api(keyword, sort, int(start), int(length))
            else:
                data = similarity.get_all_similarity_for_api(keyword, sort)
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
