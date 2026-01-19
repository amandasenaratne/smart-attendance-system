import cv2
import face_recognition
import os
import numpy as np
from pathlib import Path
import pickle


class FaceRegistration:
    """Handles face registration and encoding."""
    
    def __init__(self, faces_dir="data/datasets/faces", encodings_file="data/encodings.pkl"):
        """
        Initialize FaceRegistration.
        
        Args:
            faces_dir: Directory where face images are stored
            encodings_file: Path to store/load face encodings
        """
        self.faces_dir = faces_dir
        self.encodings_file = encodings_file
        self.known_encodings = []
        self.known_names = []
        
        os.makedirs(faces_dir, exist_ok=True)
        self._load_encodings()
    
    def capture_face(self, person_name, num_images=5):
        """
        Capture multiple face images for a person using webcam.
        
        Args:
            person_name: Name of the person
            num_images: Number of images to capture
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory for person
            person_dir = os.path.join(self.faces_dir, person_name)
            os.makedirs(person_dir, exist_ok=True)
            
            # Open webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: Could not open webcam")
                return False
            
            captured = 0
            print(f"Capturing {num_images} images for {person_name}")
            print("Press SPACE to capture, ESC to cancel")
            
            while captured < num_images:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to read frame")
                    break
                
                # Mirror the frame
                frame = cv2.flip(frame, 1)
                
                # Display frame with instructions
                cv2.putText(frame, f"Captured: {captured}/{num_images}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "SPACE to capture, ESC to cancel", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                
                cv2.imshow(f"Register Face - {person_name}", frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC
                    print("Cancelled")
                    break
                elif key == 32:  # SPACE
                    img_path = os.path.join(person_dir, f"{person_name}_{captured}.jpg")
                    cv2.imwrite(img_path, frame)
                    captured += 1
                    print(f"Captured image {captured}/{num_images}")
            
            cap.release()
            cv2.destroyAllWindows()
            
            if captured > 0:
                print(f"Successfully captured {captured} images for {person_name}")
                return True
            return False
            
        except Exception as e:
            print(f"Error capturing face: {e}")
            return False
    
    def encode_registered_faces(self):
        """
        Encode all registered faces and save encodings to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            encodings = []
            names = []
            
            print("Encoding registered faces...")
            
            # Iterate through each person's directory
            for person_name in os.listdir(self.faces_dir):
                person_dir = os.path.join(self.faces_dir, person_name)
                
                if not os.path.isdir(person_dir):
                    continue
                
                print(f"Processing {person_name}...")
                
                # Process each image for this person
                for image_name in os.listdir(person_dir):
                    image_path = os.path.join(person_dir, image_name)
                    
                    try:
                        # Load image
                        image = face_recognition.load_image_file(image_path)
                        
                        # Get face encodings
                        face_encodings = face_recognition.face_encodings(image)
                        
                        # Store the first encoding found
                        if face_encodings:
                            encodings.append(face_encodings[0])
                            names.append(person_name)
                            print(f"  Encoded: {image_name}")
                    except Exception as e:
                        print(f"  Error encoding {image_name}: {e}")
            
            # Save encodings and names
            data = {"encodings": encodings, "names": names}
            with open(self.encodings_file, "wb") as f:
                pickle.dump(data, f)
            
            self.known_encodings = encodings
            self.known_names = names
            
            print(f"Encoding complete! Total faces encoded: {len(encodings)}")
            return True
            
        except Exception as e:
            print(f"Error encoding faces: {e}")
            return False
    
    def _load_encodings(self):
        """Load pre-computed face encodings from file."""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, "rb") as f:
                    data = pickle.load(f)
                    self.known_encodings = data["encodings"]
                    self.known_names = data["names"]
                print(f"Loaded {len(self.known_encodings)} face encodings")
        except Exception as e:
            print(f"Error loading encodings: {e}")
    
    def get_registered_people(self):
        """
        Get list of registered people.
        
        Returns:
            list: List of person names
        """
        if os.path.exists(self.faces_dir):
            return [name for name in os.listdir(self.faces_dir) 
                   if os.path.isdir(os.path.join(self.faces_dir, name))]
        return []
