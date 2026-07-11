from pydantic import BaseModel
from typing import Optional


class StudentOut(BaseModel):
    id: str
    name: str
    roll_no: str


class RegisterResponse(BaseModel):
    success: bool
    message: str
    student_id: Optional[str] = None


class AttendanceMarkResponse(BaseModel):
    success: bool
    message: str
    student_name: Optional[str] = None
    roll_no: Optional[str] = None
    confidence: Optional[float] = None


class AttendanceRecord(BaseModel):
    student_id: str
    name: str
    roll_no: str
    date: str
    time: str
    status: str
