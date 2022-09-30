from src.database.database import Database
from src.api.app import run
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    api_port = os.getenv("API_PORT")
    run(port=api_port)
