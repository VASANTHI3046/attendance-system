"""
Core computer vision utilities:
- Detect a face in an uploaded image
- Generate a 128-d face encoding (face_recognition / dlib)
- Compare an unknown encoding against known encodings from Firestore
"""

import face_recognition
import numpy as np
import cv2
from typing import Optional, Tuple, List


def bytes_to_image(image_bytes: bytes):
    """Convert raw uploaded bytes into an OpenCV BGR image."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def get_face_encoding_from_image(image_bytes: bytes) -> Tuple[Optional[np.ndarray], Optional[tuple]]:
    """
    Detects the largest/first face in the image and returns its 128-d encoding.
    Returns (None, None) if no face is found.
    """
    img = bytes_to_image(image_bytes)
    if img is None:
        return None, None

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_img, model="hog")

    if len(face_locations) == 0:
        return None, None

    encodings = face_recognition.face_encodings(rgb_img, known_face_locations=face_locations)
    return encodings[0], face_locations[0]


def get_all_face_encodings(image_bytes: bytes) -> List[np.ndarray]:
    """Detects ALL faces in an image (useful for group/classroom photos)."""
    img = bytes_to_image(image_bytes)
    if img is None:
        return []

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_img, model="hog")
    if len(face_locations) == 0:
        return []

    return face_recognition.face_encodings(rgb_img, known_face_locations=face_locations)


def compare_faces(known_encodings: List[np.ndarray], unknown_encoding: np.ndarray, tolerance: float = 0.5):
    """
    Compares an unknown face encoding against a list of known encodings.
    Returns (best_match_index, distance) or (None, None) if no match within tolerance.
    """
    if not known_encodings:
        return None, None

    distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    best_match_index = int(np.argmin(distances))

    if distances[best_match_index] <= tolerance:
        return best_match_index, float(distances[best_match_index])

    return None, None
