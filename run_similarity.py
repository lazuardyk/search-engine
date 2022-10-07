from dotenv import load_dotenv
from src.overall_ranking.similarity import Similarity
from src.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()

    similarity = Similarity()
    res = similarity.get_all_similarity_for_api("klub barcelona")
