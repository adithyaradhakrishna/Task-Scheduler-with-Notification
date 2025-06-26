# Full Task Scheduler - One File Version

import tkinter as tk
from tkinter import messagebox
import sqlite3
import threading
import time
import datetime
from plyer import notification

# ----- BASE62 encode -----
BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def encode(num):
    s = []
    while num > 0:
        num, r = divmod(num, 62)
        s.append(BASE62[r])
    return ''.join(reversed(s)) or '0'

# ----- Notifications -----
def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

# ----- DB utils -----
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            due_time TEXT,
            repeat TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_task(title, description, due_time, repeat):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, description, due_time, repeat) VALUES (?, ?, ?, ?)",
                   (title, description, due_time, repeat))
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ----- GUI -----
class TaskSchedulerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler")

        tk.Label(root, text="Title").grid(row=0, column=0)
        tk.Label(root, text="Description").grid(row=1, column=0)
        tk.Label(root, text="Due Time (YYYY-MM-DD HH:MM)").grid(row=2, column=0)
        tk.Label(root, text="Repeat (once/daily/weekly)").grid(row=3, column=0)

        self.title = tk.Entry(root)
        self.desc = tk.Entry(root)
        self.due_time = tk.Entry(root)
        self.repeat = tk.Entry(root)

        self.title.grid(row=0, column=1)
        self.desc.grid(row=1, column=1)
        self.due_time.grid(row=2, column=1)
        self.repeat.grid(row=3, column=1)

        tk.Button(root, text="Add Task", command=self.add_task).grid(row=4, column=1, pady=10)

        # Start background notification thread
        threading.Thread(target=self.check_due_tasks, daemon=True).start()

    def add_task(self):
        title = self.title.get()
        desc = self.desc.get()
        due_time = self.due_time.get()
        repeat = self.repeat.get()

        add_task(title, desc, due_time, repeat)
        messagebox.showinfo("Success", "Task Added!")

    def check_due_tasks(self):
        while True:
            tasks = get_tasks()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            for task in tasks:
                task_id, title, desc, due_time, repeat = task
                if due_time == now:
                    task_code = encode(task_id)
                    send_notification(f"Task #{task_code}: {title}", desc)

            time.sleep(60)  # check every minute

# ----- Main -----
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = TaskSchedulerUI(root)
    root.mainloop()
