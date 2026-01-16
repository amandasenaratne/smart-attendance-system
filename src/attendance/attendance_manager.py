import csv
import os
from datetime import datetime
from pathlib import Path


class AttendanceManager:
    """Manages attendance records stored in CSV format."""
    
    def __init__(self, csv_file_path):
        """
        Initialize the AttendanceManager with a CSV file path.
        
        Args:
            csv_file_path: Path to the attendance records CSV file
        """
        self.csv_file_path = csv_file_path
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
            
            # Create CSV with headers
            with open(self.csv_file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Date', 'Time', 'Status'])
    
    def record_attendance(self, name, status='Present'):
        """
        Record attendance for a person.
        
        Args:
            name: Name of the person
            status: Attendance status (Present/Absent), default is Present
            
        Returns:
            bool: True if recorded successfully, False otherwise
        """
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Check if this person already has attendance recorded today
            if self._check_duplicate(name, current_date):
                return False
            
            with open(self.csv_file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([name, current_date, current_time, status])
            
            return True
        except Exception as e:
            print(f"Error recording attendance: {e}")
            return False
    
    def _check_duplicate(self, name, date):
        """
        Check if attendance is already recorded for a person on a given date.
        
        Args:
            name: Name of the person
            date: Date in YYYY-MM-DD format
            
        Returns:
            bool: True if duplicate exists, False otherwise
        """
        try:
            with open(self.csv_file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if row and row[0] == name and row[1] == date:
                        return True
            return False
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False
    
    def get_all_records(self):
        """
        Get all attendance records.
        
        Returns:
            list: List of dictionaries containing attendance records
        """
        records = []
        try:
            with open(self.csv_file_path, 'r') as f:
                reader = csv.DictReader(f, fieldnames=['Name', 'Date', 'Time', 'Status'])
                next(reader, None)  # Skip header
                for row in reader:
                    if row['Name']:  # Skip empty rows
                        records.append(row)
        except Exception as e:
            print(f"Error reading records: {e}")
        
        return records
    
    def get_records_by_date(self, date):
        """
        Get attendance records for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            list: List of dictionaries for the specified date
        """
        records = []
        try:
            with open(self.csv_file_path, 'r') as f:
                reader = csv.DictReader(f, fieldnames=['Name', 'Date', 'Time', 'Status'])
                next(reader, None)  # Skip header
                for row in reader:
                    if row['Name'] and row['Date'] == date:
                        records.append(row)
        except Exception as e:
            print(f"Error reading records by date: {e}")
        
        return records
    
    def get_records_by_person(self, name):
        """
        Get all attendance records for a specific person.
        
        Args:
            name: Name of the person
            
        Returns:
            list: List of dictionaries for the specified person
        """
        records = []
        try:
            with open(self.csv_file_path, 'r') as f:
                reader = csv.DictReader(f, fieldnames=['Name', 'Date', 'Time', 'Status'])
                next(reader, None)  # Skip header
                for row in reader:
                    if row['Name'] == name:
                        records.append(row)
        except Exception as e:
            print(f"Error reading records by person: {e}")
        
        return records
    
    def export_to_csv(self, export_path):
        """
        Export all records to a specified CSV file.
        
        Args:
            export_path: Path where to export the CSV file
            
        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            records = self.get_all_records()
            
            with open(export_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Date', 'Time', 'Status'])
                for record in records:
                    writer.writerow([
                        record['Name'],
                        record['Date'],
                        record['Time'],
                        record['Status']
                    ])
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_summary_statistics(self):
        """
        Get summary statistics of attendance.
        
        Returns:
            dict: Dictionary containing summary statistics
        """
        records = self.get_all_records()
        stats = {
            'total_records': len(records),
            'unique_persons': len(set(r['Name'] for r in records if r['Name'])),
            'present_count': len([r for r in records if r['Status'] == 'Present']),
            'absent_count': len([r for r in records if r['Status'] == 'Absent'])
        }
        return stats
