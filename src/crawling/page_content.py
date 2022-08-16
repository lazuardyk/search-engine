import pymysql
from src.database.database import Database


class PageContent:
    """
    Kelas yang berisi fungsi-fungsi untuk menyimpan konten halaman web ke database.
    """

    def insert_page_form(self, db_connection: pymysql.Connection, url: str, form: str) -> None:
        """
        Fungsi untuk menyimpan form yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            form (str): Form halaman
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_forms` (`url`, `form`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, form))
        db_cursor.close()

    def insert_page_image(self, db_connection: pymysql.Connection, url: str, image: str) -> None:
        """
        Fungsi untuk menyimpan gambar yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            image (str): Image halaman
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_images` (`url`, `image`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, image))
        db_cursor.close()

    def insert_page_information(
        self,
        db_connection: pymysql.Connection,
        url: str,
        crawl_id: int,
        html5: bool,
        title: str,
        description: str,
        keywords: str,
        content_text: str,
        hot_url: bool,
        model_crawl: str,
    ) -> None:
        """
        Fungsi untuk menyimpan konten seperti teks, judul, deskripsi yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            crawl_id (int): ID crawling
            html5 (bool): Versi html5, 1 jika ya, 0 jika tidak
            title (str): Judul halaman
            description (str): Deskripsi  halaman
            keywords (str): Keyword halaman
            content_text (str): Konten teks halaman
            hot_url (bool): Hot URL, 1 jika ya, 0 jika tidak
            model_crawl (str): Model crawling yaitu BFS atau MSB
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_information` (`url`, `crawl_id`, `html5`, `title`, `description`, `keywords`, `content_text`, `hot_url`, `model_crawl`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        db_cursor.execute(
            query, (url, crawl_id, html5, title, description, keywords, content_text, hot_url, model_crawl)
        )
        db_cursor.close()

    def set_hot_url(self, db_connection: pymysql.Connection, url: str, hot_link: bool) -> None:
        """
        Fungsi untuk menandakan hot URL pada halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            hot_link (bool): Hot URL, 1 jika ya, 0 jika tidak
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "UPDATE `page_information` SET `hot_url` = %s WHERE `url` = %s"
        db_cursor.execute(query, (url, hot_link))
        db_cursor.close()

    def insert_page_linking(
        self, db_connection: pymysql.Connection, crawl_id: int, url: str, outgoing_link: str
    ) -> None:
        """
        Fungsi untuk menyimpan url linking yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            crawl_id (int): ID crawling
            url (str): URL halaman
            outgoing_link (str): Outgoing link
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_linking` (`crawl_id`, `url`, `outgoing_link`) VALUES (%s, %s, %s)"
        db_cursor.execute(query, (crawl_id, url, outgoing_link))
        db_cursor.close()

    def insert_page_list(self, db_connection: pymysql.Connection, url: str, list: str) -> None:
        """
        Fungsi untuk menyimpan list yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            list (str): List halaman
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_list` (`url`, `list`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, list))
        db_cursor.close()

    def insert_page_script(self, db_connection: pymysql.Connection, url: str, script: str) -> None:
        """
        Fungsi untuk menyimpan script yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            script (str): Script halaman
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_scripts` (`url`, `script`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, script))
        db_cursor.close()

    def insert_page_style(self, db_connection: pymysql.Connection, url: str, style: str) -> None:
        """
        Fungsi untuk menyimpan style yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            style (str): Style halaman
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_styles` (`url`, `style`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, style))
        db_cursor.close()

    def insert_page_table(self, db_connection: pymysql.Connection, url: str, table: str) -> None:
        """
        Fungsi untuk menyimpan table yang ada di halaman web ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            table (str): Table halaman
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_tables` (`url`, `table_str`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, table))
        db_cursor.close()

    def insert_crawling(
        self, db_connection: pymysql.Connection, url: str, keyword: str, total_page: int, duration: int
    ) -> int:
        """
        Fungsi untuk menyimpan data crawling yang sudah dilakukan ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): URL halaman
            keyword (str): Keyword yang dipakai
            total_page (int): Jumlah halaman
            duration (int): Total durasi

        Returns:
            int: ID crawling dari baris yang disimpan
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `crawling` (`start_url`, `keyword`, `total_page`, `duration_crawl`) VALUES (%s, %s, %s, SEC_TO_TIME(%s))"
        db_cursor.execute(query, (url, keyword, total_page, duration))
        inserted_id = db_cursor.lastrowid
        db_cursor.close()
        return inserted_id

    def update_crawling(self, db_connection: pymysql.Connection, crawl_id: int, total_page: int) -> None:
        """
        Fungsi untuk memperbarui data crawling ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            crawl_id (int): ID crawling
            total_page (int): Jumlah halaman
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "UPDATE `crawling` SET `total_page` = %s WHERE `id_crawling` = %s"
        db_cursor.execute(query, (total_page, crawl_id))
        db_cursor.close()

    def get_visited_urls(self, db_connection: pymysql.Connection) -> list:
        """
        Fungsi untuk mendapatkan kumpulan URL yang sudah pernah di crawl dari database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL

        Returns:
            list: Kumpulan URL yang pernah dicrawl
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "SELECT url FROM `page_information`"
        db_cursor.execute(query)
        row_arr = []
        for row in db_cursor.fetchall():
            row_arr.append(row[0])
        db_cursor.close()
        return row_arr
