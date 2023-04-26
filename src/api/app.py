from flask import Flask, render_template, request
import os


def run():
    app = Flask(__name__)

    from src.api.crawling import bp_crawling
    from src.api.page_ranking import bp_page_ranking
    from src.api.document_ranking import bp_document_ranking
    from src.api.overall_ranking import bp_overall_ranking
    from src.api.indexing import bp_indexing

    api_version = os.getenv("API_VERSION")
    app.register_blueprint(
        bp_crawling, url_prefix="/api/" + api_version + "/crawling")
    app.register_blueprint(
        bp_page_ranking, url_prefix="/api/" + api_version + "/page_ranking")
    app.register_blueprint(
        bp_document_ranking, url_prefix="/api/" + api_version + "/document_ranking")
    app.register_blueprint(
        bp_overall_ranking, url_prefix="/api/" + api_version + "/overall_ranking")
    app.register_blueprint(
        bp_indexing, url_prefix="/api/" + api_version + "/indexing")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
