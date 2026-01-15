# attendance_manager.py - placeholder
import csv
import os
from attendance.attendance_utils import get_today_date, get_current_time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance_records.csv")


def ensure_file():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Date", "Time"])


def already_marked(name, date):
    if not os.path.exists(ATTENDANCE_FILE):
        return False

    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] == name and row[1] == date:
                return True
    return False


def mark_attendance(name):
    ensure_file()

    today = get_today_date()
    time_now = get_current_time()

    if already_marked(name, today):
        print(f"{name} already marked today")
        return False

    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, today, time_now])

    print(f"Attendance marked for {name}")
    return True


