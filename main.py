import tkinter.font

from db_manager import db_manager
from data_gen import *
import tkinter as tk
from tkinter import ttk


class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent


class LoginApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        '''
        self.selected_teacher = tk.StringVar()
        self.select_teacher_cb = ttk.Combobox(self, textvariable=self.selected_teacher)
        self.select_teacher_cb["state"] = "readonly"
        self.select_teacher_cb.pack(fill=tk.X, padx=5, pady=50, anchor=tk.N)

        query = db_manager.run_query("select * from teachers order by last_name asc", expected_return=True)
        teachers = []
        for row in query:
            name = row[2] + ' ' + row[1]
            teachers.append(f"{name : <30} {row[3]}")
        self.select_teacher_cb["values"] = teachers
        '''

        self.upper_frame = ttk.Frame(self, style="LoginApp.TFrame")
        self.upper_frame.pack(side="top", expand=True, fill="both", padx=5, pady=5)

        ttk.Label(self.upper_frame, text="First name").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.upper_frame, text="Last name").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.upper_frame, text="Email").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.fname = tk.StringVar()
        self.fname_en = ttk.Entry(self.upper_frame, textvariable=self.fname)
        self.fname_en.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)

        self.lname = tk.StringVar()
        self.lname_en = ttk.Entry(self.upper_frame, textvariable=self.lname)
        self.lname_en.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

        self.email = tk.StringVar()
        self.email_en = ttk.Entry(self.upper_frame, textvariable=self.email)
        self.email_en.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

        self.login_btn = ttk.Button(self, text="Login", command=self.login)
        self.login_btn.pack(side="bottom", expand=True, fill="both", padx=5, pady=5)

    def login(self):
        query = f"select count(*) from teachers where first_name = '{self.fname.get()}' and last_name = '{self.lname.get()}' and teacher_email = '{self.email.get()}'"
        can_login = bool(db_manager.run_query(query, expected_return=True)[0][0])
        if can_login:
            global logged_email
            logged_email = self.email.get()
            open_main_app()


def open_main_app():
    login_app.pack_forget()
    login_app.destroy()
    root.quit()


root = tk.Tk()

style = ttk.Style()
style.configure("LoginApp.TFrame", background="red")

root.title("GradeBook Login")
login_app = LoginApp(root, height=200, width=300)
login_app.pack_propagate(False)
login_app.pack(side="top", fill="both", expand=True)
logged_email = ""

root.mainloop()

root.title("GradeBook")
main_app = MainApp(root, height=600, width=900)
main_app.pack(side="top", fill="both", expand=True)

root.mainloop()
