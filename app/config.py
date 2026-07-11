import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
FACE_MATCH_TOLERANCE = float(os.getenv("FACE_MATCH_TOLERANCE", "0.5"))
