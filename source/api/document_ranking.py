from flask import Blueprint, request
from source.document_ranking.tf_idf import TfIdf
import json

bp_document_ranking = Blueprint(
    "document_ranking",
    __name__,
)


@bp_document_ranking.route("/tf_idf")
def get_tf_idf_ranks():
    try:
        keyword = request.args.get("keyword", default="", type=str)
        start = request.args.get("start", default="", type=str)
        length = request.args.get("length", default="", type=str)

        tf_idf = TfIdf()
        if keyword == "":
            response = {
                "ok": False,
                "message": "Keyword tidak ada. Masukkan keyword pada url seperti '?keyword=barcelona'",
            }
        else:
            if start != "" and length != "":
                data = tf_idf.get_all_tfidf_for_api(keyword, int(start), int(length))
            else:
                data = tf_idf.get_all_tfidf_for_api(keyword)
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
