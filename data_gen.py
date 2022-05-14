from os import chdir
from random import randint
from abc import ABC, abstractmethod
from db_manager import db_manager
import config


class TableData(ABC):
    @staticmethod
    @abstractmethod
    def generate(rows_amount):
        pass  # generates random data

    @staticmethod
    @abstractmethod
    def table_name():
        pass  # returns name of table

    @staticmethod
    @abstractmethod
    def insert(*args):
        pass  # insert data to table

    @classmethod
    def get_columns(cls):
        tables = []
        for column_data in db_manager.run_query(f"pragma table_info({cls.table_name()})", expected_return=True):
            tables.append(list(column_data)[1])
        tables.pop(0)  # pk autoincrement
        return tuple(tables)

    @classmethod
    def clear(cls):
        db_manager.run_query(f"delete from {cls.table_name()}")
        db_manager.run_query(f"delete from sqlite_sequence where name = '{cls.table_name()}'")


class ParentsData(TableData):
    @staticmethod
    def generate(rows_amount):
        for _ in range(rows_amount):
            father = Identity(gender="male")
            mother = Identity(gender="female", last_name=father.last_name)
            ParentsData.insert(father.first_name, father.email, mother.first_name, mother.email)

    @staticmethod
    def table_name():
        return "parents"

    @staticmethod
    def insert(father_name, father_email, mother_name, mother_email):
        db_manager.run_query(f"insert into parents values " +
                             f"(null, '{father_name}', '{father_email}', '{mother_name}', '{mother_email}')")


class TeachersData(TableData):
    @staticmethod
    def generate(rows_amount):
        for _ in range(rows_amount):
            if randint(0, 1):
                teacher = Identity("male")
            else:
                teacher = Identity("female")
            TeachersData.insert(teacher.first_name, teacher.last_name, teacher.email)

    @staticmethod
    def table_name():
        return "teachers"

    @staticmethod
    def insert(first_name, last_name, teacher_email):
        db_manager.run_query(f"insert into teachers values " +
                             f"(null, '{first_name}', '{last_name}', '{teacher_email}')")


class ClassData(TableData):
    class_profiles_org = list(config.SUBJECTS.keys())

    @staticmethod
    def generate(rows_amount, with_existing_teachers=False):
        if with_existing_teachers:
            max_rows_amount = int(db_manager.run_query(f"select count(*) from teachers", expected_return=True)[0][0])
            rows_amount = min(rows_amount, max_rows_amount)

        for _ in range(rows_amount):
            class_profiles = ClassData.class_profiles_org[:]
            class_profile_1 = class_profiles.pop(randint(0, len(class_profiles) - 1))
            class_profile_2 = class_profiles.pop(randint(0, len(class_profiles) - 1))
            class_name = f"{randint(1, 8)} {class_profile_1}-{class_profile_2}"
            if with_existing_teachers:
                available_ids = db_manager.run_query(
                    f"select teacher_id from teachers where teacher_id not in (select teacher_id from classes)",
                    expected_return=True)
                teacher_id = available_ids[0][0]
            else:
                TeachersData.generate(1)
                teacher_id = db_manager.run_query(f"select teacher_id from teachers order by teacher_id desc limit 1",
                                                  expected_return=True)[0][0]
            ClassData.insert(class_name, teacher_id)

    @staticmethod
    def table_name():
        return "classes"

    @staticmethod
    def insert(class_name, teacher_id):
        db_manager.run_query(f"insert into classes values " +
                             f"(null, '{class_name}', '{teacher_id}')")


class StudentsData(TableData):
    @staticmethod
    def generate(rows_amount, with_existing_parents=False, with_existing_classes=False):
        if with_existing_parents:
            max_rows_amount = int(db_manager.run_query(
                f"select count(parents_id) from parents where parents_id not in (select parents_id from students)",
                expected_return=True)[0][0])
            rows_amount = min(rows_amount, max_rows_amount)

        for _ in range(rows_amount):
            student = Identity()
            if with_existing_parents:
                parents_id = int(db_manager.run_query(
                    f"select parents_id from parents where parents_id not in (select parents_id from students) limit 1",
                    expected_return=True)[0][0])
            else:
                ParentsData.generate(1)
                parents_id = db_manager.run_query(f"select parents_id from parents order by parents_id desc limit 1",
                                                  expected_return=True)[0][0]

            if with_existing_classes:
                class_amount = int(db_manager.run_query(
                    f"select count(class_id) from classes", expected_return=True)[0][0])

                class_id = db_manager.run_query(
                    f"select class_id from classes order by class_id", expected_return=True)[randint(0, class_amount - 1)][0]
            else:
                ClassData.generate(1)
                class_id = db_manager.run_query(f"select class_id from classes order by class_id desc limit 1",
                                                expected_return=True)[0][0]

            StudentsData.insert(student.first_name, student.last_name, student.email, class_id, parents_id)

    @staticmethod
    def table_name():
        return "students"

    @staticmethod
    def insert(first_name, last_name, student_email, class_id, parents_id):
        db_manager.run_query(f"insert into students values " +
                             f"(null, '{first_name}', '{last_name}', '{student_email}', '{class_id}', '{parents_id}')")


class GradesData(TableData):
    lesson_names_org = list(config.SUBJECTS.keys())

    @staticmethod
    def generate(rows_amount, with_existing_students=False):
        lesson_names = GradesData.lesson_names_org[:]
        for _ in range(rows_amount):
            if with_existing_students:
                students_amount = int(db_manager.run_query(
                    f"select count(student_id) from students",
                    expected_return=True)[0][0])

                student_id = int(db_manager.run_query(
                    f"select student_id from students",
                    expected_return=True)[randint(0, students_amount - 1)][0])
            else:
                StudentsData.generate(1)
                student_id = db_manager.run_query(f"select student_id from students order by student_id desc limit 1", expected_return=True)[0][0]

            value = randint(1, 6)
            lesson_name = lesson_names[randint(0, len(lesson_names) - 1)]
            GradesData.insert(student_id, lesson_name, value)

    @staticmethod
    def table_name():
        return "grades"

    @staticmethod
    def insert(student_id, lesson_name, value):
        db_manager.run_query(f"insert into grades values " +
                             f"(null, '{student_id}', '{lesson_name}', '{value}', '1')")


class Identity:
    def __init__(self, gender=None, last_name=None):
        if gender is None and randint(0, 1):
            self.gender = "male"
        elif gender is None:
            self.gender = "female"
        else:
            self.gender = gender

        try:
            chdir(config.DATA_GEN_FILES_PATH)
        except FileNotFoundError:
            chdir(config.DATA_GEN_FILES_PATH_LINUX)

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


def gen_all():
    ParentsData.clear()
    TeachersData.clear()
    ClassData.clear()
    StudentsData.clear()
    GradesData.clear()

    ClassData.generate(10)
    StudentsData.generate(200, with_existing_classes=True)
    GradesData.generate(10000, with_existing_students=True)

# gen_all()
