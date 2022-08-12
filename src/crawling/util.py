from urllib.parse import urlparse
import requests


class Util:
    def count_keyword_in_text(self, text, keyword):
        """Fungsi untuk menghitung keyword yang muncul dalam suatu teks."""
        count_keyword = text.count(keyword)
        return count_keyword

    def is_valid_url(self, url):
        """Fungsi untuk mengecek apakah sebuah URL valid atau tidak."""
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"] and bool(parsed.netloc)

    def get_page(self, url):
        """Fungsi untuk melakukan permintaan (request) ke URL."""
        try:
            res = requests.get(url, verify=False, timeout=300)
            res.raise_for_status()
            return res
        except Exception as e:
            print(e)
            return

    def running_thread_count(self, futures):
        """Fungsi untuk menghitung berapa threads yang sedang berjalan."""
        r = 0
        for future in futures:
            if future.running():
                r += 1
        print(f"{r} threads running")
        return r
