import pymysql
import os

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")

    def connect(self):
        connection = pymysql.connect(host = self.host, user = self.username, passwd = self.password, db = self.db_name, autocommit = True)
        return connection
    
    def close_connection(self, connection):
        try:
            connection.close()
        except:
            pass
    
    def check_value_in_table(self, connection, table_name, column_name, value):
        connection.ping()
        db_cursor = connection.cursor()
        db_cursor.execute("SELECT {column}, COUNT(*) FROM {table} WHERE {column} = '{value}' GROUP BY {column}".format(table=table_name, column=column_name, value=value))
        db_cursor.fetchall()
        row_count = db_cursor.rowcount
        db_cursor.close()
        if row_count < 1:
            return False
        return True
    
    def count_rows(self, connection, table_name):
        connection.ping()
        db_cursor = connection.cursor()
        db_cursor.execute("SELECT COUNT(*) FROM {table}".format(table=table_name))
        row_count = db_cursor.fetchone()[0]
        db_cursor.close()
        return row_count

    def exec_query(self, connection, query):
        connection.ping()
        db_cursor = connection.cursor()
        db_cursor.execute(query)
        db_cursor.close()
    
    def create_crawler_tables(self, connection):
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS crawling (id_crawling INT PRIMARY KEY AUTO_INCREMENT, start_url TEXT, keyword TEXT, total_page INT, duration_crawl TIME, created_at TIMESTAMP)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_forms (id_form INT PRIMARY KEY AUTO_INCREMENT, url TEXT, form TEXT)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_images (id_image INT PRIMARY KEY AUTO_INCREMENT, url TEXT, image TEXT)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_linking (id_linking INT PRIMARY KEY AUTO_INCREMENT, crawl_id INT, url TEXT, outgoing_link TEXT)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_list (id_list INT PRIMARY KEY AUTO_INCREMENT, url TEXT, list TEXT)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_information (id_information INT PRIMARY KEY AUTO_INCREMENT, crawl_id INT, url TEXT, html5 TINYINT, title TEXT, description TEXT, keywords TEXT, content_text TEXT, hot_url TINYINT, model_crawl TEXT, created_at TIMESTAMP)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_scripts (id_script INT PRIMARY KEY AUTO_INCREMENT, url TEXT, script TEXT)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_styles (id_style INT PRIMARY KEY AUTO_INCREMENT, url TEXT, style TEXT)")
        self.exec_query(connection, "CREATE TABLE IF NOT EXISTS page_tables (id_table INT PRIMARY KEY AUTO_INCREMENT, url TEXT, table_str TEXT)")