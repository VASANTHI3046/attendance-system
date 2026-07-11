from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from datetime import datetime
import numpy as np

from app.firebase_config import db, STUDENTS_COLLECTION, ATTENDANCE_COLLECTION
from app.face_utils import get_face_encoding_from_image, compare_faces
from app.models import AttendanceMarkResponse, AttendanceRecord
from app.config import FACE_MATCH_TOLERANCE

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def _load_known_students():
    """Pull all students + their stored encodings from Firestore."""
    docs = db.collection(STUDENTS_COLLECTION).stream()
    ids, names, rolls, encodings = [], [], [], []
    for doc in docs:
        data = doc.to_dict()
        ids.append(doc.id)
        names.append(data.get("name"))
        rolls.append(data.get("roll_no"))
        encodings.append(np.array(data.get("encoding")))
    return ids, names, rolls, encodings


@router.post("/mark", response_model=AttendanceMarkResponse)
async def mark_attendance(file: UploadFile = File(...)):
    """
    Send a single frame (e.g. captured from a classroom camera).
    The detected face is compared against all registered students.
    If matched, attendance is marked in Firestore for today's date
    (only once per student per day).
    """
    image_bytes = await file.read()

    unknown_encoding, _ = get_face_encoding_from_image(image_bytes)
    if unknown_encoding is None:
        raise HTTPException(status_code=400, detail="No face detected in the frame.")

    ids, names, rolls, encodings = _load_known_students()
    if not encodings:
        raise HTTPException(status_code=400, detail="No students registered yet.")

    match_index, distance = compare_faces(encodings, unknown_encoding, tolerance=FACE_MATCH_TOLERANCE)

    if match_index is None:
        return AttendanceMarkResponse(success=False, message="Face not recognized.")

    student_id = ids[match_index]
    name = names[match_index]
    roll_no = rolls[match_index]

    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    # Avoid marking the same student twice on the same day
    attendance_doc_id = f"{student_id}_{today}"
    doc_ref = db.collection(ATTENDANCE_COLLECTION).document(attendance_doc_id)

    if doc_ref.get().exists:
        return AttendanceMarkResponse(
            success=True,
            message=f"{name} already marked present today.",
            student_name=name,
            roll_no=roll_no,
            confidence=round(1 - distance, 3),
        )

    doc_ref.set({
        "student_id": student_id,
        "name": name,
        "roll_no": roll_no,
        "date": today,
        "time": now_time,
        "status": "present",
    })

    return AttendanceMarkResponse(
        success=True,
        message=f"Attendance marked for {name}.",
        student_name=name,
        roll_no=roll_no,
        confidence=round(1 - distance, 3),
    )


@router.get("/{date}", response_model=List[AttendanceRecord])
async def get_attendance_by_date(date: str):
    """
    Get attendance for a specific date. Format: YYYY-MM-DD
    """
    docs = db.collection(ATTENDANCE_COLLECTION).where("date", "==", date).stream()
    records = []
    for doc in docs:
        data = doc.to_dict()
        records.append(AttendanceRecord(**data))
    return records
