from dotenv import load_dotenv
from source.document_ranking.tf_idf import TfIdf
from source.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    tf_idf = TfIdf()
    res = tf_idf.run_background_service()
