from sqlite3 import connect
from typing import List, Any

import config


class DbManager:
    def __init__(self):
        self.db_name = config.DB_FILE_NAME
        self.conn = connect(self.db_name)
        self.cursor = self.conn.cursor()

    def run_query(self, query: str, expected_return: bool = False) -> 'None or List':
        if expected_return:
            print(f"SQL QUERY: {query}")
            return self.cursor.execute(query).fetchall()
        else:
            print(f"SQL QUERY: {query}")
            self.cursor.execute(query)
            self.conn.commit()


db_manager = DbManager()
db_cursor = db_manager.cursor
db_connection = db_manager.conn
