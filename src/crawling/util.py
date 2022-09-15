from typing import Any
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor
import queue


class Util:
    """
    Kelas yang berisi fungsi-fungsi utilitas crawler.
    """

    def count_keyword_in_text(self, text: str, keyword: str) -> int:
        """
        Fungsi untuk menghitung keyword yang muncul dalam suatu teks.

        Args:
            text (str): Input teks
            keyword (str): Keyword yang ingin dihitung

        Returns:
            int: Jumlah keyword yang ada di dalam teks
        """
        count_keyword = text.count(keyword)
        return count_keyword

    def is_valid_url(self, url: str) -> bool:
        """
        Fungsi untuk mengecek apakah sebuah URL valid atau tidak.

        Args:
            url (str): URL halaman

        Returns:
            bool: True jika URL valid, False jika tidak
        """
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"] and bool(parsed.netloc)

    def get_page(self, url: str) -> Any:
        """
        Fungsi untuk melakukan permintaan (request) ke URL.

        Args:
            url (str): URL halaman

        Returns:
            Any: Respons dari halaman. None jika error
        """
        try:
            res = requests.get(url, verify=False, timeout=300)
            res.raise_for_status()
            return res
        except Exception as e:
            print(e)
            return

    def running_thread_count(self, futures: list) -> int:
        """
        Fungsi untuk menghitung berapa threads yang sedang berjalan.

        Args:
            futures (list): Kumpulan objek future

        Returns:
            int: Jumlah threads yang sedang berjalan
        """
        r = 0
        for future in futures:
            if future.running():
                r += 1
        print(f"{r} threads running")
        return r


class CustomThreadPoolExecutor(ThreadPoolExecutor):
    """
    Kelas yang inherit dari ThreadPoolExecutor untuk menambahkan metode custom shutdown.
    Referensi: https://tiewkh.github.io/blog/python-thread-pool-executor/
    """

    def shutdown39(self, wait=True, *, cancel_futures=False):
        with self._shutdown_lock:
            self._shutdown = True
            if cancel_futures:
                # Drain all work items from the queue, and then cancel their
                # associated futures.
                while True:
                    try:
                        work_item = self._work_queue.get_nowait()
                    except queue.Empty:
                        break
                    if work_item is not None:
                        work_item.future.cancel()

            # Send a wake-up to prevent threads calling
            # _work_queue.get(block=True) from permanently blocking.
            self._work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()
