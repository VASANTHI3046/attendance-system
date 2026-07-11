from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import students, attendance

app = FastAPI(
    title="CV-based Attendance System",
    description="Face recognition attendance system using FastAPI + Firebase",
    version="1.0.0",
)

# Allow requests from any frontend / camera client during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(attendance.router)


@app.get("/")
async def root():
    return {"message": "Face Recognition Attendance System API is running. Visit /docs for Swagger UI."}
