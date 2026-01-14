import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from face_registration.register_face import FaceRegistration


def encode_all_faces():
    """
    Main function to encode all registered faces.
    
    Run this after registering faces to generate encodings.pkl
    """
    print("Face Encoding System")
    print("=" * 50)
    
    # Initialize face registration
    registration = FaceRegistration(
        faces_dir="data/datasets/faces",
        encodings_file="data/encodings.pkl"
    )
    
    # Encode all registered faces
    success = registration.encode_registered_faces()
    
    if success:
        print("\nEncoding completed successfully!")
        print(f"Total faces encoded: {len(registration.known_encodings)}")
    else:
        print("Encoding failed!")
    
    return success


if __name__ == "__main__":
    encode_all_faces()
