from flask import Blueprint, request
from src.database.database import Database
from src.document_ranking.tf_idf import TfIdf
import pymysql

bp_document_ranking = Blueprint(
    "document_ranking",
    __name__,
)


@bp_document_ranking.route("/tf_idf")
def get_tf_idf_ranks():
    try:
        keyword = request.args.get("keyword", default="", type=str)

        tf_idf = TfIdf()
        if keyword == "":
            return {
                "ok": False,
                "message": "Keyword tidak ada. Masukkan keyword pada url seperti '?keyword=barcelona'",
                "data": [],
            }
        else:
            data = tf_idf.run(keyword)
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


@bp_document_ranking.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
