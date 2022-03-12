from sqlite3 import *
import config


class DbManager:
    def __init__(self):
        self.db_name = config.DB_FILE_NAME
        self.conn = connect(self.db_name)
        self.cursor = self.conn.cursor()

    def run_query(self, query: str) -> None:
        self.cursor.execute(query)
        self.conn.commit()
        print(f"SQL QUERY: {query}")


db_manager = DbManager()
db_cursor = db_manager.cursor
db_connection = db_manager.conn
