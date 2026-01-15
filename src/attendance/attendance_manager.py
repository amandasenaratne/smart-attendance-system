import csv
import os
from datetime import datetime

class AttendanceManager:
    def __init__(self, records_file):
        self.records_file = records_file
        # Ensure the CSV file exists and has headers
        if not os.path.exists(self.records_file):
            with open(self.records_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Date', 'Time'])

    def mark_attendance(self, name):
        """Mark attendance for a recognized person if not already marked today."""
        today = datetime.now().strftime('%Y-%m-%d')
        if not self.is_present_today(name, today):
            now = datetime.now().strftime('%H:%M:%S')
            with open(self.records_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, today, now])
            return True
        return False

    def is_present_today(self, name, date=None):
        """Check if the person is already marked present for the given date (default: today)."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if not os.path.exists(self.records_file):
            return False
        with open(self.records_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Name'] == name and row['Date'] == date:
                    return True
        return False

    def get_attendance_for_date(self, date=None):
        """Return a list of names who are present for the given date (default: today)."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        attendees = []
        if not os.path.exists(self.records_file):
            return attendees
        with open(self.records_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Date'] == date:
                    attendees.append(row['Name'])
        return attendees

if __name__ == "__main__":
    # Test mode for AttendanceManager
    records_path = os.path.join(os.path.dirname(__file__), "attendance_records.csv")
    manager = AttendanceManager(records_path)
    print("Testing attendance system...")
    name = input("Enter name to mark attendance: ")
    if manager.mark_attendance(name):
        print(f"Attendance marked for {name}.")
    else:
        print(f"{name} has already marked attendance today.")
    print("Today's attendees:")
    attendees = manager.get_attendance_for_date()
    for attendee in attendees:
        print(attendee)
