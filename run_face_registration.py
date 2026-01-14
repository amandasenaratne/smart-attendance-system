import sys
import os

# Add the 'src' folder to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Now import the class from the file
from face_registration.register_face import FaceRegistration


def main():
    fr = FaceRegistration()

    name = input("Enter person name: ").strip()
    if not name:
        print("Name cannot be empty")
        return

    fr.capture_face(person_name=name, num_images=5)
    fr.encode_registered_faces()

    print("Registered users:", fr.get_registered_people())


if __name__ == "__main__":
    main()
