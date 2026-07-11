import firebase_admin
from firebase_admin import credentials, firestore

from app.config import FIREBASE_CREDENTIALS_PATH

# Initialize Firebase Admin SDK only once
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

STUDENTS_COLLECTION = "students"
ATTENDANCE_COLLECTION = "attendance"
