from os import chdir
from random import randint
from abc import ABC, abstractmethod
from db_manager import db_cursor, db_connection, db_manager
import config


class TableData(ABC):
    @staticmethod
    @abstractmethod
    def generate_data(rows_amount: int) -> None:
        pass

    @staticmethod
    @abstractmethod
    def table_name() -> str:
        pass

    @classmethod
    def get_columns(cls) -> tuple:
        tables = []
        for column_data in db_cursor.execute(f"pragma table_info({cls.table_name()})"):
            tables.append(list(column_data)[1])
        tables.pop(0)  # pk autoincrement
        return tuple(tables)

    @classmethod
    def clear_table(cls) -> None:
        db_manager.run_query(f"delete from {cls.table_name()}")
        db_manager.run_query(f"delete from sqlite_sequence where name = '{cls.table_name()}'")


class ParentsData(TableData):
    @staticmethod
    def generate_data(rows_amount: int) -> None:
        for _ in range(rows_amount):
            father = Identity("male")
            mother = Identity("female", last_name=father.last_name)
            ParentsData.insert_parents(father.first_name, father.email, mother.first_name, mother.email)

    @staticmethod
    def table_name() -> str:
        return "parents"

    @staticmethod
    def insert_parents(father_name: str, father_email: str, mother_name: str, mother_email: str) -> None:
        db_manager.run_query(f"insert into parents values " +
                             f"(null, '{father_name}', '{father_email}', '{mother_name}', '{mother_email}')")


class TeachersData(TableData):
    @staticmethod
    def generate_data(rows_amount: int) -> None:
        for _ in range(rows_amount):
            if randint(0, 1):
                teacher = Identity("male")
            else:
                teacher = Identity("female")
            TeachersData.insert_teacher(teacher.first_name, teacher.last_name, teacher.email)

    @staticmethod
    def table_name() -> str:
        return "teachers"

    @staticmethod
    def insert_teacher(first_name: str, last_name: str, teacher_email: str) -> None:
        db_manager.run_query(f"insert into teachers values " +
                             f"(null, '{first_name}', '{last_name}', '{teacher_email}')")


class Identity:
    def __init__(self, gender: str, last_name: str = None):
        self.gender = gender  # male / female
        chdir(config.DATA_GEN_FILES_PATH)

        if last_name is None:
            with open("last_names.txt", encoding="utf8") as last_names:
                self.last_name = last_names.readlines()[randint(0, config.LAST_NAMES - 1)].replace("\n", "")
        else:
            self.last_name = last_name

        if self.gender == "male":
            with open("first_names_m.txt", encoding="utf8") as first_names:
                self.first_name = first_names.readlines()[randint(0, config.FIRST_NAMES_MALE - 1)].replace("\n", "")

        else:
            with open("first_names_f.txt", encoding="utf8") as first_names:
                self.first_name = first_names.readlines()[randint(0, config.FIRST_NAMES_FEMALE - 1)].replace("\n", "")
            if "ki" in self.last_name:
                self.last_name = self.last_name.replace("ki", "ka")

        self.email = f"{self.first_name}.{self.last_name}{randint(0, 999)}@{chr(randint(ord('a'), ord('z')))}_mail.com".lower()

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email}"


ParentsData.clear_table()
TeachersData.clear_table()
ParentsData.generate_data(100)
TeachersData.generate_data(100)
