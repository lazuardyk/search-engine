from dotenv import load_dotenv
from source.page_ranking.page_rank import PageRank
from source.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    page_rank = PageRank()
    page_rank.run_background_service()
