#! /opt/rh/rh-python38/root/usr/bin/python

import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
sys.path.insert(0, "/var/www/html/search-engine")
sys.stdout = open("output.logs", "w")

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)
logging.info(os.environ)

from src.api.app import run
from src.database.database import Database

db = Database()
db.create_tables()
application = run()
