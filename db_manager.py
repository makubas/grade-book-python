from sqlite3 import connect
import config


class DbManager:
    def __init__(self):
        self.db_name = config.DB_FILE_NAME
        self.conn = connect(self.db_name)
        self.cursor = self.conn.cursor()

    def run_query(self, query, expected_return=False):
        if ';' in query:  # catching sql injection
            raise ValueError("Can't use ';'")
        if expected_return:
            print(f"SQL QUERY: {query}")
            return self.cursor.execute(query).fetchall()
        else:
            print(f"SQL QUERY: {query}")
            self.cursor.execute(query)
        self.conn.commit()

    def erase_table_data(self, *tables):
        for table in tables:
            self.run_query(f"delete from {table}")
            self.run_query(f"delete from sqlite_sequence where name = '{table}'")

    def erase_all_data(self):
        self.erase_table_data("classes", "grades", "parents", "students", "teachers")


db_manager = DbManager()
db_cursor = db_manager.cursor
db_connection = db_manager.conn
