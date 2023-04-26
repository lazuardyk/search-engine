from flask import Blueprint, request
from src.indexing.gst import main
import json

bp_indexing = Blueprint(
    "indexing",
    __name__,
)


@bp_indexing.route('/gstsearch', methods=['POST'])
def gstsearch():
    query = request.form['query']
    response = main(query)
    return response
