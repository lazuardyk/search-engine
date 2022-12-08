from dotenv import load_dotenv
from src.page_ranking.page_rank import run_background_service
from src.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    run_background_service()
