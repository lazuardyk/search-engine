from flask import Flask, render_template, request
import os


def run():
    app = Flask(__name__)

    from source.api.crawling import bp_crawling
    from source.api.page_ranking import bp_page_ranking
    from source.api.document_ranking import bp_document_ranking
    from source.api.overall_ranking import bp_overall_ranking

    api_version = os.getenv("API_VERSION")
    app.register_blueprint(bp_crawling, url_prefix="/api/" + api_version + "/crawling")
    app.register_blueprint(bp_page_ranking, url_prefix="/api/" + api_version + "/page_ranking")
    app.register_blueprint(bp_document_ranking, url_prefix="/api/" + api_version + "/document_ranking")
    app.register_blueprint(bp_overall_ranking, url_prefix="/api/" + api_version + "/overall_ranking")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
