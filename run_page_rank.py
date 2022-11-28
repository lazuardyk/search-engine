from dotenv import load_dotenv
from src.page_ranking.page_rank import PageRank
from src.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    try:
        connection = db.connect()
        db.exec_query(
            connection,
            "CREATE TABLE `pagerank_changes` ( `id_change` int PRIMARY KEY AUTO_INCREMENT, `page_id` int, `iteration` int, `pagerank_change` double )",
        )
        db.exec_query(
            connection,
            "ALTER TABLE `pagerank_changes` ADD FOREIGN KEY (`page_id`) REFERENCES `page_information` (`id_page`)",
        )
    except Exception as e:
        pass

    page_rank = PageRank()
    page_rank.run_background_service()
