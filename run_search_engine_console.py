from dotenv import load_dotenv
from src.overall_ranking.similarity import get_all_similarity_for_api
from src.database.database import Database
from src.crawling.crawl_utils import CrawlUtils

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    crawl_utils = CrawlUtils()

    keyword = input("Input keyword pencarian: ")

    similarity_results = get_all_similarity_for_api(keyword, "similarity", 0, 100)
    id_pages = [res["id_page"] for res in similarity_results]

    search_results_str = "Hasil pencarian:\n\n"

    if len(id_pages) > 0:
        page_information_list = crawl_utils.get_page_information_by_ids(id_pages)
        for i in range(len(similarity_results)):
            similarity_result = similarity_results[i]
            for page_information in page_information_list:
                if page_information["id_page"] != similarity_result["id_page"]:
                    continue
                if page_information["title"]:
                    search_results_str += str(i + 1) + ". " + page_information["title"].strip() + "\n"
                else:
                    continue
                if page_information["url"]:
                    search_results_str += page_information["url"].strip() + "\n"
                # if page_information["description"]:
                #     search_results_str += page_information["description"].strip() + "\n\n"
                if page_information["content_text"]:
                    search_results_str += page_information["content_text"].strip()[0:100] + "\n\n"
    else:
        search_results_str += "Tidak ada hasil"

    print(search_results_str)
