import os
import sys
import webbrowser
import subprocess
import time


# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Try to import face recognition modules, but provide fallback
try:
    from face_registration.register_face import FaceRegistration
    from face_recognition.recognize_faces import FaceRecognizer
    from face_recognition.encode_faces import encode_all_faces
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


def main_menu():
    """Main menu for the Smart Attendance System."""
    
    while True:
        print("\n" + "=" * 60)
        print("SMART ATTENDANCE SYSTEM - Main Menu")
        print("=" * 60)
        print("1. Register New Person (Capture Face Images)")
        print("2. Encode Registered Faces (Generate Face Encodings)")
        print("3. Start Face Recognition Attendance Mode")
        print("4. View Registered People")
        print("5. Open Dashboard (http://localhost:5000)")
        print("6. View Attendance Records (CSV)")
        print("7. Exit")
        print("=" * 60)
        
        if not FACE_RECOGNITION_AVAILABLE:
            print("\nNOTE: Face recognition features (1-4) require additional dependencies.")
            print("Please install: opencv-python, face-recognition, numpy")
            print("\nDashboard and CSV viewing are available.")
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            if FACE_RECOGNITION_AVAILABLE:
                register_person()
            else:
                print("Face recognition not available. Please install dependencies.")
        elif choice == "2":
            if FACE_RECOGNITION_AVAILABLE:
                encode_faces()
            else:
                print("Face recognition not available. Please install dependencies.")
        elif choice == "3":
            if FACE_RECOGNITION_AVAILABLE:
                start_recognition()
            else:
                print("Face recognition not available. Please install dependencies.")
        elif choice == "4":
            if FACE_RECOGNITION_AVAILABLE:
                view_registered_people()
            else:
                print("Face recognition not available. Please install dependencies.")
        elif choice == "5":
            open_dashboard()
        elif choice == "6":
            view_csv()
        elif choice == "7":
            print("Exiting Smart Attendance System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def register_person():
    """Register a new person's face."""
    print("\n" + "-" * 60)
    print("REGISTER NEW PERSON")
    print("-" * 60)
    
    person_name = input("Enter person's name: ").strip()
    if not person_name:
        print("Name cannot be empty!")
        return
    
    try:
        num_images = int(input("Enter number of images to capture (default 5): ") or "5")
    except ValueError:
        num_images = 5
    
    registration = FaceRegistration(
        faces_dir="data/datasets/faces",
        encodings_file="data/encodings.pkl"
    )
    
    success = registration.capture_face(person_name, num_images)
    
    if success:
        print(f"\nSuccessfully registered {person_name}!")
        print("Next: Encode faces (Option 2) to update face encodings")
    else:
        print(f"Failed to register {person_name}")


def encode_faces():
    """Encode all registered faces."""
    print("\n" + "-" * 60)
    print("ENCODE REGISTERED FACES")
    print("-" * 60)
    print("This will process all registered face images and create encodings...")
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return
    
    success = encode_all_faces()
    if success:
        print("Face encodings have been updated successfully!")


def start_recognition():
    """Start real-time face recognition for attendance."""
    print("\n" + "-" * 60)
    print("FACE RECOGNITION ATTENDANCE MODE")
    print("-" * 60)
    
    recognizer = FaceRecognizer(
        encodings_file="data/encodings.pkl",
        csv_path="src/attendance/attendance_records.csv"
    )
    
    if not recognizer.known_encodings:
        print("No face encodings found!")
        print("Please register faces first (Option 1) and encode them (Option 2)")
        return
    
    print(f"Loaded {len(recognizer.known_encodings)} face encodings")
    print("Starting webcam face recognition...\n")
    
    recognizer.start_attendance_mode()


def view_registered_people():
    """View all registered people."""
    print("\n" + "-" * 60)
    print("REGISTERED PEOPLE")
    print("-" * 60)
    
    registration = FaceRegistration(
        faces_dir="data/datasets/faces",
        encodings_file="data/encodings.pkl"
    )
    
    people = registration.get_registered_people()
    
    if not people:
        print("No registered people found!")
    else:
        print(f"Total registered people: {len(people)}\n")
        for i, person in enumerate(people, 1):
            person_dir = os.path.join("data/datasets/faces", person)
            image_count = len([f for f in os.listdir(person_dir) 
                             if f.endswith(('.jpg', '.jpeg', '.png'))])
            print(f"{i}. {person} ({image_count} images)")


def open_dashboard():
    """Open the dashboard in browser."""
    print("\n" + "-" * 60)
    print("OPEN DASHBOARD")
    print("-" * 60)
    print("\nOpening dashboard in browser...")
    print("URL: http://localhost:5000")
    
    try:
        webbrowser.open('http://localhost:5000')
        print("Browser opened successfully!")
    except Exception as e:
        print(f"Could not open browser: {e}")
        print("Please open http://localhost:5000 manually in your browser")


def view_csv():
    """View attendance records from CSV."""
    print("\n" + "-" * 60)
    print("ATTENDANCE RECORDS")
    print("-" * 60)
    
    csv_path = "src/attendance/attendance_records.csv"
    
    try:
        if not os.path.exists(csv_path):
            print("No attendance records found yet.")
            return
        
        with open(csv_path, 'r') as f:
            lines = f.readlines()
        
        if len(lines) <= 1:
            print("No attendance records yet.")
            return
        
        print("\nAttendance Records:\n")
        print(f"{'Name':<20} {'Date':<12} {'Time':<10} {'Status':<10}")
        print("-" * 52)
        
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 4:
                name, date, time, status = parts[0], parts[1], parts[2], parts[3]
                print(f"{name:<20} {date:<12} {time:<10} {status:<10}")
        
        print(f"\nTotal records: {len(lines) - 1}")
        
    except Exception as e:
        print(f"Error reading CSV: {e}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")

