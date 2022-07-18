from app.database import Database

class PageContent:
    
    def insert_page_form(self, db_connection, url, form):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_forms` (`url`, `form`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, form))
        db_cursor.close()
    
    def insert_page_image(self, db_connection, url, image):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_images` (`url`, `image`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, image))
        db_cursor.close()
    
    def insert_page_information(self, db_connection, url, crawl_id, html5, title, description, keywords, content_text, hot_url, model_crawl):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_information` (`url`, `crawl_id`, `html5`, `title`, `description`, `keywords`, `content_text`, `hot_url`, `model_crawl`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        db_cursor.execute(query, (url, crawl_id, html5, title, description, keywords, content_text, hot_url, model_crawl))
        db_cursor.close()
    
    def set_hot_url(self, db_connection, url, hot_link):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "UPDATE `page_information` SET `hot_url` = %s WHERE `url` = %s"
        db_cursor.execute(query, (url, hot_link))
        db_cursor.close()

    def insert_page_linking(self, db_connection, crawl_id, url, outgoing_link):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_linking` (`crawl_id`, `url`, `outgoing_link`) VALUES (%s, %s, %s)"
        db_cursor.execute(query, (crawl_id, url, outgoing_link))
        db_cursor.close()
    
    def insert_page_list(self, db_connection, url, list):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_list` (`url`, `list`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, list))
        db_cursor.close()
    
    def insert_page_script(self, db_connection, url, script):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_scripts` (`url`, `script`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, script))
        db_cursor.close()
    
    def insert_page_style(self, db_connection, url, style):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_styles` (`url`, `style`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, style))
        db_cursor.close()
    
    def insert_page_table(self, db_connection, url, table):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `page_tables` (`url`, `table_str`) VALUES (%s, %s)"
        db_cursor.execute(query, (url, table))
        db_cursor.close()
    
    def insert_crawling(self, db_connection, url, keyword, total_page, duration):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `crawling` (`start_url`, `keyword`, `total_page`, `duration_crawl`) VALUES (%s, %s, %s, %s)"
        db_cursor.execute(query, (url, keyword, total_page, duration))
        inserted_id = db_cursor.lastrowid
        db_cursor.close()
        return inserted_id
    
    def update_crawling(self, db_connection, crawl_id, total_page):
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "UPDATE `crawling` SET `total_page` = %s WHERE `id_crawling` = %s"
        db_cursor.execute(query, (total_page, crawl_id))
        db_cursor.close()