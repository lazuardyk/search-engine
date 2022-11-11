#! /opt/rh/rh-python38/root/usr/bin/python

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/search-engine")
# sys.stdout = open('output.logs', 'w')
from source.api.app import run
from source.database.database import Database
from dotenv import load_dotenv

load_dotenv(dotenv_path="/var/www/html/search-engine/.env")
db = Database()
db.create_tables()
application = run()
