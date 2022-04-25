from data_gen import *
import config
import tkinter as tk
from tkinter import ttk

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
        self.selected_class_cb = ttk.Combobox(self.filters_frame, textvariable=self.selected_class_var, state="readonly", values=self.classes_list)
        self.selected_class_cb.pack(side="left", **padxy)

        # Subjects
        ttk.Label(self.filters_frame, text="Subjects:").pack(side="left", **padxy)

        self.subject_cb_var = tk.StringVar(value="All")
        self.subject_cb = ttk.Combobox(self.filters_frame, textvariable=self.subject_cb_var, state="readonly", values=["All", "Only selected"])
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
        self.treeview.get_data_about_class(self.selected_class_var)

    def filter(self):
        pass

    def subject_cb_update(self, event):
        is_all = (self.subject_cb_var.get() == "All")
        for comobox in self.subject_chbtns.values():
            comobox.subject_cb_var.set(is_all)


class SubjectCheckbutton(ttk.Checkbutton):
    def __init__(self, parent, shown_text):
        self.subject_cb_var = tk.BooleanVar(value=False)
        ttk.Checkbutton.__init__(self, parent, text=shown_text, variable=self.subject_cb_var, onvalue=True, offvalue=False, command=self.on_click)

    def on_click(self):
        pass

    def selected(self):
        return self.subject_cb_var.get()


class StudentsTreeview(ttk.Treeview):
    columns = {
        "id": "Id",
        "last_name": "Last name",
        "first_name": "First name"
    }

    def __init__(self, parent, *args, **kwargs):
        ttk.Treeview.__init__(self, parent, *args, show="headings", columns=list(self.columns.keys()), **kwargs)
        for column, heading in self.columns.items():
            self.add_column(column, heading)
        self.column("id", width=40)
        self.column("last_name", width=100)
        self.column("first_name", width=100)

    def add_column(self, column, heading):
        self.heading(column, text=heading)

    def get_data_about_class(self, class_name):
        query = f"select * from students where class_id in (select class_id from classes where class_name='{class_name}')"
        data = db_manager.run_query(query, expected_return=True)
        print(data)


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
