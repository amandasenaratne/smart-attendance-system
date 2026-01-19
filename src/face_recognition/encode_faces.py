# encode_faces.py - build and save face encodings
import os
import pickle

from typing import List, Tuple

import numpy as np
from PIL import Image, ImageOps

try:
    import face_recognition
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
    ) from e


DATASET_DIR = "data/datasets/faces"
ENCODINGS_PATH = "data/encodings/face_encodings.pkl"

def load_image_rgb_fixed(image_path: str) -> np.ndarray:
    """Load an image as RGB and fix EXIF orientation (common on iPhone photos)."""
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    return np.array(img)


def load_face_images(dataset_dir: str) -> Tuple[List[str], List[str]]:
    """
    Reads images from the dataset directory.
    Expected structure:
    dataset_dir/person_name/image.jpg
    """
    image_paths = []
    names = []

    for person_name in os.listdir(dataset_dir):
        person_path = os.path.join(dataset_dir, person_name)

        if not os.path.isdir(person_path):
            continue

        for image_name in os.listdir(person_path):
            image_path = os.path.join(person_path, image_name)

            if image_name.lower().endswith((".jpg", ".png", ".jpeg")):
                image_paths.append(image_path)
                names.append(person_name)

    return image_paths, names


def generate_encodings(image_paths, names):
    """
    Generates face encodings for given images.
    """
    encodings = []
    valid_names = []

    for image_path, name in zip(image_paths, names):
        image = load_image_rgb_fixed(image_path)
        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=1, model="hog")

        if len(face_locations) == 0:
            print(f"[WARN] No face detected in: {image_path}")
            continue  # skip images without faces

        try:
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
        except Exception as ex:
            print(f"[WARN] Failed to encode face in: {image_path} ({ex})")
            continue

        encodings.append(face_encoding)
        valid_names.append(name)

    return encodings, valid_names


def save_encodings(encodings, names, output_path):
    """
    Saves encodings as a pickle file.
    """
    data = {
        "encodings": encodings,
        "names": names
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as file:
        pickle.dump(data, file)


def build_face_encodings():
    """
    Main function to build and save face encodings.
    """
    image_paths, names = load_face_images(DATASET_DIR)
    print(f"[INFO] Images found: {len(image_paths)}")
    if image_paths:
        print(f"[INFO] Sample image: {image_paths[0]}")
    encodings, valid_names = generate_encodings(image_paths, names)
    if len(encodings) == 0:
        print("[ERROR] No encodings were generated. Common causes: images are too small/dark, faces not front-facing, or iPhone EXIF rotation.")
        print("[ERROR] Try using a clear, front-facing selfie where the face fills ~30-60% of the image.")
    save_encodings(encodings, valid_names, ENCODINGS_PATH)

    print(f"[INFO] Encodings saved to {ENCODINGS_PATH}")
    print(f"[INFO] Total faces encoded: {len(encodings)}")


if __name__ == "__main__":
    build_face_encodings()
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
