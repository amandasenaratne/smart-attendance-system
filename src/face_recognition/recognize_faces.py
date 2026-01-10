import cv2
import face_recognition
import numpy as np
import pickle
import os
from datetime import datetime
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from attendance.attendance_manager import AttendanceManager


class FaceRecognizer:
    """Handles real-time face recognition and attendance marking."""
    
    def __init__(self, encodings_file="data/encodings.pkl", 
                 csv_path="src/attendance/attendance_records.csv"):
        """
        Initialize FaceRecognizer.
        
        Args:
            encodings_file: Path to saved face encodings
            csv_path: Path to attendance records CSV
        """
        self.encodings_file = encodings_file
        self.known_encodings = []
        self.known_names = []
        self.attendance_manager = AttendanceManager(csv_path)
        self.marked_today = set()
        
        self._load_encodings()
    
    def _load_encodings(self):
        """Load pre-computed face encodings."""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, "rb") as f:
                    data = pickle.load(f)
                    self.known_encodings = data["encodings"]
                    self.known_names = data["names"]
                print(f"Loaded {len(self.known_encodings)} face encodings")
            else:
                print("No encodings file found. Register faces first.")
        except Exception as e:
            print(f"Error loading encodings: {e}")
    
    def recognize_face(self, frame):
        """
        Recognize faces in a frame.
        
        Args:
            frame: Video frame from webcam
            
        Returns:
            tuple: (face_locations, face_encodings, names_with_confidence)
        """
        try:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find faces and encodings in current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            confidences = []
            
            # Compare faces
            for face_encoding in face_encodings:
                # Calculate face distances
                face_distances = face_recognition.face_distance(
                    self.known_encodings, face_encoding
                )
                
                # Find best match
                best_match_index = np.argmin(face_distances)
                confidence = 1 - face_distances[best_match_index]
                
                if confidence > 0.6:  # Confidence threshold
                    name = self.known_names[best_match_index]
                else:
                    name = "Unknown"
                
                face_names.append(name)
                confidences.append(confidence)
            
            return face_locations, face_names, confidences
            
        except Exception as e:
            print(f"Error recognizing face: {e}")
            return [], [], []
    
    def start_attendance_mode(self):
        """
        Start real-time face recognition for attendance marking.
        
        Press 'M' to mark attendance, 'Q' to quit
        """
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: Could not open webcam")
                return
            
            print("Starting Face Recognition for Attendance")
            print("Press 'M' to mark attendance, 'Q' to quit")
            print("=" * 50)
            
            process_this_frame = True
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to read frame")
                    break
                
                # Mirror frame
                frame = cv2.flip(frame, 1)
                
                # Process every other frame for speed
                if process_this_frame:
                    face_locations, face_names, confidences = self.recognize_face(frame)
                
                process_this_frame = not process_this_frame
                
                # Display results
                self._display_faces(frame, face_locations, face_names, confidences)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):  # Quit
                    print("Exiting...")
                    break
                elif key == ord('m'):  # Mark attendance
                    for name, confidence in zip(face_names, confidences):
                        if name != "Unknown" and confidence > 0.6:
                            self._mark_attendance(name)
            
            cap.release()
            cv2.destroyAllWindows()
            
            print("\nAttendance Summary:")
            print(f"Marked attendance for: {', '.join(self.marked_today)}")
            
        except Exception as e:
            print(f"Error in attendance mode: {e}")
    
    def _display_faces(self, frame, face_locations, face_names, confidences):
        """Display recognized faces on frame."""
        try:
            for (top, right, bottom, left), name, confidence in zip(
                face_locations, face_names, confidences
            ):
                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Determine color based on recognition
                if name == "Unknown":
                    color = (0, 0, 255)  # Red for unknown
                    label = f"{name}"
                else:
                    color = (0, 255, 0)  # Green for recognized
                    label = f"{name} ({confidence:.2f})"
                
                # Draw rectangle
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label background
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, label, (left + 6, bottom - 6),
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            # Display instructions
            cv2.putText(frame, "Press 'M' to mark, 'Q' to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Marked: {len(self.marked_today)} people", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Face Recognition - Attendance", frame)
            
        except Exception as e:
            print(f"Error displaying faces: {e}")
    
    def _mark_attendance(self, name):
        """Mark attendance for recognized person."""
        try:
            if name not in self.marked_today:
                success = self.attendance_manager.record_attendance(name, "Present")
                if success:
                    self.marked_today.add(name)
                    print(f"Marked attendance for: {name}")
                else:
                    print(f"Could not mark attendance for {name} (already marked or error)")
        except Exception as e:
            print(f"Error marking attendance: {e}")

