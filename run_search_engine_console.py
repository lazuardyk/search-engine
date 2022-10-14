from dotenv import load_dotenv
from src.overall_ranking.similarity import Similarity
from src.database.database import Database
from src.crawling.crawl_utils import CrawlUtils

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    similarity = Similarity()
    crawl_utils = CrawlUtils()

    keyword = input("Input keyword pencarian: ")

    similarity_results = similarity.get_all_similarity_for_api(keyword, "similarity", 0, 100)
    id_pages = [res["id_page"] for res in similarity_results]
    page_information_list = crawl_utils.get_page_information_by_ids(id_pages)

    search_results_str = "Hasil pencarian:\n\n"
    for i in range(len(similarity_results)):
        similarity_result = similarity_results[i]
        page_information = page_information_list[i]
        search_results_str += str(i + 1) + ". " + page_information["title"] + "\n"
        search_results_str += page_information["url"] + "\n"
        search_results_str += page_information["description"] + "\n\n"

    print(search_results_str)
