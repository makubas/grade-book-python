from data_gen import *
import config
import tkinter as tk
from tkinter import ttk
import pprint


class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Frames
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, **padxy)

        self.filters_frame = ttk.Frame(self.main_frame)
        self.filters_frame.pack(fill="x", side="top")

        self.treeview_frame = ttk.Frame(self.main_frame)
        self.treeview_frame.pack(fill="both", expand=True, side="bottom")

        # Classes
        ttk.Label(self.filters_frame, text="Class:").pack(side="left", **padxy)

        self.selected_class_var = tk.StringVar()
        self.curr_teacher_classes = []
        for classes in db_manager.run_query(f"select class_name from classes inner join teachers on classes.teacher_id = teachers.teacher_id where teacher_email='{logged_email}'", expected_return=True):
            self.curr_teacher_classes.append(classes[0])

        self.classes_list = []
        for class_name in db_manager.run_query("select class_name from classes", expected_return=True):
            if class_name[0] in self.curr_teacher_classes:
                self.classes_list.append(class_name[0] + "   [YOUR CLASS]")
            else:
                self.classes_list.append(class_name[0])
        self.classes_list.sort(key=lambda class_nm: class_nm[0])

        self.selected_class_cb = ttk.Combobox(self.filters_frame, width=25, textvariable=self.selected_class_var, state="readonly", values=self.classes_list)
        self.selected_class_cb.pack(side="left", **padxy)

        # Subjects
        ttk.Label(self.filters_frame, text="Subjects:").pack(side="left", **padxy)

        self.subject_cb_var = tk.StringVar(value="Only selected")
        self.subject_cb = ttk.Combobox(self.filters_frame, width=15, textvariable=self.subject_cb_var, state="readonly", values=["All", "Only selected"])
        self.subject_cb.bind("<<ComboboxSelected>>", self.subject_cb_update)
        self.subject_cb.pack(side="left", **padxy)

        self.subject_chbtns = {}
        for subj_key, subj_name in config.SUBJECTS.items():
            subject_chbtn = SubjectCheckbutton(self.filters_frame, subj_name)
            self.subject_chbtns[subj_key] = subject_chbtn
            subject_chbtn.pack(side="left", **padxy)

        self.filter_btn = ttk.Button(self.filters_frame, text="Filter", command=self.filter)
        self.filter_btn.pack(side="left", **padxy)

        # Treeview
        self.treeview = StudentsTreeview(self.treeview_frame)
        self.treeview.pack(fill="both", expand=True, **padxy)

    def filter(self):
        self.treeview.reload()

    def subject_cb_update(self, event):
        is_all = (self.subject_cb_var.get() == "All")
        for comobox in self.subject_chbtns.values():
            comobox.subject_cb_var.set(is_all)

    def subjects_to_show(self):
        subjects = []
        for subject_id, subject_chbtn in self.subject_chbtns.items():
            if subject_chbtn.is_selected():
                subjects.append(subject_id)
        return subjects


class SubjectCheckbutton(ttk.Checkbutton):
    def __init__(self, parent, shown_text):
        self.subject_cb_var = tk.BooleanVar(value=False)
        ttk.Checkbutton.__init__(self, parent, text=shown_text, variable=self.subject_cb_var, onvalue=True, offvalue=False)

    def is_selected(self):
        return self.subject_cb_var.get()


class StudentsTreeview(ttk.Treeview):
    columns = {
        **{
            "id": "Id",
            "last_name": "Last name",
            "first_name": "First name"
        },
        **config.SUBJECTS
    }

    def __init__(self, parent, *args, **kwargs):
        ttk.Treeview.__init__(self, parent, *args, show="headings", columns=list(self.columns.keys()), **kwargs)
        print(self.columns)
        self.data = {}
        for column, heading in self.columns.items():
            self.heading(column, text=heading)
        self.column("id", width=40)
        self.column("last_name", width=100)
        self.column("first_name", width=100)

    def reload(self):
        query = f"select student_id, last_name, first_name from students where class_id in (select class_id from classes where class_name = '{main_app.selected_class_var.get()}') order by last_name "
        class_data = db_manager.run_query(query, expected_return=True)
        for row in class_data:
            student_id = row[0]
            grades = {}

            for subject in config.SUBJECTS.keys():
                grades[subject] = []
            for grade in db_manager.run_query(f"select lesson_name, value, weight from grades where student_id = '{student_id}'", expected_return=True):
                grades[grade[0]].append(grade[1])

            '''
            for subject in config.SUBJECTS.keys():
                grades[subject] = []
            for grade in db_manager.run_query(f"select lesson_name, value, weight from grades where student_id = '{student_id}'", expected_return=True):
                grades[grade[0]].append({
                    "value": grade[1],
                    "weight": grade[2]
                })
            '''

            self.data[student_id] = grades
            self.data[student_id]["info"] = {
                "last_name": row[1],
                "first_name": row[2]
            }

        pp.pprint(self.data)

        display_columns = list(self["columns"])
        for column in self.columns.keys():
            if column not in main_app.subjects_to_show() and column not in ["id", "last_name", "first_name"]:
                display_columns.remove(column)
                pass
        self["displaycolumns"] = display_columns

        self.delete(*self.get_children())
        for student_id, student_data in self.data.items():
            insert_data = [student_id, student_data["info"]["last_name"], student_data["info"]["first_name"]]
            for subj_id in config.SUBJECTS.keys():
                insert_data.append(student_data[subj_id])
            self.insert(parent="", index="end", text=student_data["info"]["last_name"]+student_data["info"]["first_name"], values=insert_data)


class LoginApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.upper_frame = ttk.Frame(self, style="LoginApp.TFrame")
        self.upper_frame.pack(side="top", fill="x", **padxy)

        self.upper_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.upper_frame, text="First name").grid(row=0, column=0, sticky=tk.W, **padxy)
        ttk.Label(self.upper_frame, text="Last name").grid(row=1, column=0,sticky=tk.W, **padxy)
        ttk.Label(self.upper_frame, text="Email").grid(row=2, column=0, sticky=tk.W, **padxy)

        self.fname = tk.StringVar()
        self.fname_en = ttk.Entry(self.upper_frame, textvariable=self.fname)
        self.fname_en.grid(row=0, column=1, sticky=tk.EW, **padxy)

        self.lname = tk.StringVar()
        self.lname_en = ttk.Entry(self.upper_frame, textvariable=self.lname)
        self.lname_en.grid(row=1, column=1, sticky=tk.EW, **padxy)

        self.email = tk.StringVar()
        self.email_en = ttk.Entry(self.upper_frame, textvariable=self.email)
        self.email_en.grid(row=2, column=1, sticky=tk.EW, **padxy)

        self.login_btn = ttk.Button(self, text="Login", command=self.login)
        self.login_btn.pack(side="bottom", expand=True, fill="both", **padxy)

        if config.AUTOLOGIN:
            data = config.AUTOLOGIN_DATA
            self.fname_en.insert(0, data["first_name"])
            self.lname_en.insert(0, data["last_name"])
            self.email_en.insert(0, data["email"])

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

pp = pprint.PrettyPrinter(depth=5)
style = ttk.Style()
style.configure("LoginApp.TFrame")
padxy = {
    "padx": 5,
    "pady": 5
}

root.title("GradeBook Login")
login_app = LoginApp(root, height=180, width=330)
login_app.pack_propagate(False)
login_app.pack(side="top", fill="both", expand=True)
logged_email = ""

root.mainloop()

root.title("GradeBook")
main_app = MainApp(root, height=200, width=300)
main_app.pack(side="top", fill="both", expand=True)

root.mainloop()
