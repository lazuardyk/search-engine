from source.database.database import Database
from source.api.app import run
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    api_port = os.getenv("API_PORT")
    application = run()
    application.run(port=api_port)
