from dotenv import load_dotenv
from src.page_ranking.page_rank import PageRank

if __name__ == "__main__":
    load_dotenv()

    tfIdf = PageRank()
    tfIdf.run()