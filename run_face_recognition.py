import cv2
import face_recognition
import pickle
from pathlib import Path
from datetime import datetime
import sys
import os


# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import your AttendanceManager
from attendance.attendance_manager import AttendanceManager

# Paths
ENCODINGS_FILE = "data/encodings.pkl"
ATTENDANCE_FILE = "src/attendance/attendance_records.csv"

# Initialize AttendanceManager
attendance_manager = AttendanceManager(ATTENDANCE_FILE)

# Load known face encodings
with open(ENCODINGS_FILE, "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

print("Press ESC to exit")
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = small_frame[:, :, ::-1]  # BGR → RGB

    # Detect faces and encodings
    face_locations = face_recognition.face_locations(rgb_small)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

            # Record attendance using your AttendanceManager
            recorded = attendance_manager.record_attendance(name)
            if recorded:
                print(f"Attendance recorded for {name}")
            else:
                print(f"{name}'s attendance already recorded today")

        # Draw rectangle around face
        top, right, bottom, left = [v * 4 for v in face_location]  # Scale back
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Face Recognition", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
