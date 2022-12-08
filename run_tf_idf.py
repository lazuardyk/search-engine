from dotenv import load_dotenv
from src.document_ranking.tf_idf import run_background_service
from src.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    res = run_background_service()
