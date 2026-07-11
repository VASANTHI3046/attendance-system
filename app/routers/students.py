from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid

from app.firebase_config import db, STUDENTS_COLLECTION
from app.face_utils import get_face_encoding_from_image
from app.models import RegisterResponse, StudentOut

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/register", response_model=RegisterResponse)
async def register_student(
    name: str = Form(...),
    roll_no: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Register a new student: upload one clear photo of their face.
    The face is encoded (128-d vector) and stored in Firestore
    along with the student's name and roll number.
    """
    image_bytes = await file.read()

    encoding, _ = get_face_encoding_from_image(image_bytes)
    if encoding is None:
        raise HTTPException(status_code=400, detail="No face detected in the uploaded image. Please upload a clear front-facing photo.")

    # Prevent duplicate roll numbers
    existing = db.collection(STUDENTS_COLLECTION).where("roll_no", "==", roll_no).get()
    if len(existing) > 0:
        raise HTTPException(status_code=400, detail=f"A student with roll_no '{roll_no}' already exists.")

    student_id = str(uuid.uuid4())
    db.collection(STUDENTS_COLLECTION).document(student_id).set({
        "name": name,
        "roll_no": roll_no,
        "encoding": encoding.tolist(),  # Firestore can't store numpy arrays, so convert to list
    })

    return RegisterResponse(success=True, message="Student registered successfully.", student_id=student_id)


@router.get("/", response_model=List[StudentOut])
async def list_students():
    """List all registered students."""
    docs = db.collection(STUDENTS_COLLECTION).stream()
    students = []
    for doc in docs:
        data = doc.to_dict()
        students.append(StudentOut(id=doc.id, name=data.get("name"), roll_no=data.get("roll_no")))
    return students


@router.delete("/{student_id}")
async def delete_student(student_id: str):
    """Remove a student from the database."""
    doc_ref = db.collection(STUDENTS_COLLECTION).document(student_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Student not found.")
    doc_ref.delete()
    return {"success": True, "message": "Student deleted."}
