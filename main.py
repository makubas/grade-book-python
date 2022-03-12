from sqlite3 import *


con = connect("GradeBook.db")

for student_data in con.cursor().execute("select id, last_name from students"):
    print(f"{student_data[1]}'s grades:")
    for student_grades in con.cursor().execute(f"select value from grades where id={student_data[0]}"):
        print(student_grades[0])
    print("")

con.cursor().execute(f"pragma table_info(parents)")