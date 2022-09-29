from dotenv import load_dotenv
from src.page_ranking.page_rank import PageRank
from src.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()

    page_rank = PageRank()
    page_rank.run_background_service()
