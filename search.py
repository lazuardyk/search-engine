from dotenv import load_dotenv
from src.document_ranking.tf_idf import TfIdf

if __name__ == "__main__":
    load_dotenv()

    tfIdf = TfIdf()
    tfIdf.run(keyword="real madrid") 