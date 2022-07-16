from dotenv import load_dotenv
from app.crawl import Crawl

if __name__ == "__main__":
    load_dotenv()
    # start_url = input("Masukkan url awal: ")
    # keyword = input("Masukkan keyword: ")
    # duration = input("Masukkan durasi (dalam detik): ")
    # core_total = input("Masukkan total thread yang ingin dipakai: ")
    # c = Crawl(start_url=start_url, keyword=keyword, duration=duration, core_total=core_total)

    c = Crawl(start_urls=["https://www.indosport.com", "https://detik.com", "https://www.curiouscuisiniere.com"], max_threads="10")
    c.run()