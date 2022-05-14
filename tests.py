from data_gen import *

db_manager.erase_all_data()

''' Odczyt wszystkich nauczycieli z imieniem Anna
query = db_manager.run_query("select * from teachers where first_name = 'Anna'", expected_return=True)
for row in query:
    print(row)
'''

''' Dodanie nauczyciela i odczyt wszystkich którzy zaczynają się na T
TeachersData.insert('Testtttttttt', 'Nazwiskooooo', 'jakisemail@email.com')
query = db_manager.run_query("select * from teachers where first_name like 'T%' order by first_name", expected_return=True)
for row in query:
    print(row)
'''

''' Próba sql injection 1
TeachersData.insert('Testtttttttt', 'Nazwiskooooo', "jakisemail@email.com'); delete from teachers")
query = db_manager.run_query("select * from teachers where first_name like 'T%' order by first_name", expected_return=True)
for row in query:
    print(row)
'''

''' Próba sql injection 2
query = db_manager.run_query("select * from teachers where first_name like 'A%'; delete from teachers", expected_return=True)
for row in query:
    print(row)
'''

'''
GradesData.generate(300)
query = db_manager.run_query("select * from grades where value = 6", expected_return=True)
for row in query:
    print(row)

print("######################################################")

query = db_manager.run_query("select * from students where student_id in (select student_id from grades where value = 6)", expected_return=True)
for row in query:
    print(row)
'''

