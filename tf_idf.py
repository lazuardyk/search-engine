from dotenv import load_dotenv
from src.document_ranking.tf_idf import TfIdf
from src.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()

    tf_idf = TfIdf()
    res = tf_idf.run_background_service()
