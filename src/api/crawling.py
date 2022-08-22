from flask import Blueprint

bp_crawling = Blueprint("crawling", __name__)


@bp_crawling.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
