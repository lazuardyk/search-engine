from dotenv import load_dotenv
from source.overall_ranking.similarity import Similarity
from source.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    similarity = Similarity()
    res = similarity.get_all_similarity_for_api("klub barcelona")
