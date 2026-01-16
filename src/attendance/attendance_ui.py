import tkinter as tk
from tkinter import messagebox
import os

try:
    from attendance_manager import AttendanceManager
except ImportError:
    messagebox.showerror("Import Error", "attendance_manager.py not found in the same directory.")
    raise

# Path to your CSV file
records_path = os.path.join(os.path.dirname(__file__), "attendance_records.csv")
manager = AttendanceManager(records_path)

def mark_attendance():
    name = name_entry.get().strip()
    if not name:
        status_var.set("Please enter a name.")
        return
    if manager.mark_attendance(name):
        status_var.set(f"Attendance marked for {name}.")
        update_attendees()
    else:
        status_var.set(f"{name} has already marked attendance today.")
    name_entry.delete(0, tk.END)

def update_attendees():
    attendees = manager.get_attendance_for_date()
    attendees_list.delete(0, tk.END)
    for attendee in attendees:
        attendees_list.insert(tk.END, attendee)

def clear_entry():
    name_entry.delete(0, tk.END)
    status_var.set("")

root = tk.Tk()
root.title("Smart Attendance System")
root.resizable(False, False)

# Center the window on the screen
window_width = 350
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Header
header = tk.Label(root, text="Smart Attendance System", font=("Arial", 16, "bold"), fg="#2c3e50")
header.pack(pady=10)

# Name entry
entry_frame = tk.Frame(root)
entry_frame.pack(pady=5)
tk.Label(entry_frame, text="Enter Name:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
name_entry = tk.Entry(entry_frame, font=("Arial", 12), width=18)
name_entry.pack(side=tk.LEFT, padx=5)
clear_btn = tk.Button(entry_frame, text="Clear", command=clear_entry)
clear_btn.pack(side=tk.LEFT, padx=5)

# Mark button
mark_btn = tk.Button(root, text="Mark Attendance", font=("Arial", 12), bg="#27ae60", fg="white", command=mark_attendance)
mark_btn.pack(pady=10)

# Attendees list
tk.Label(root, text="Today's Attendees:", font=("Arial", 12, "underline")).pack(pady=5)
attendees_list = tk.Listbox(root, width=30, height=10, font=("Arial", 11))
attendees_list.pack(pady=5)

# Status bar
status_var = tk.StringVar()
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, fg="#2980b9")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

update_attendees()
root.mainloop()