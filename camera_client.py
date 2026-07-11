"""
Simple webcam client for the attendance system.

Run this on the machine connected to the classroom camera.
It captures a frame every few seconds, sends it to the FastAPI
/attendance/mark endpoint, and shows the recognition result live
on screen.

Usage:
    python camera_client.py
"""

import cv2
import requests
import time

API_URL = "http://127.0.0.1:8000/attendance/mark"
CAPTURE_INTERVAL_SECONDS = 3  # how often to send a frame for recognition

cap = cv2.VideoCapture(0)
last_sent = 0
last_message = ""

if not cap.isOpened():
    raise RuntimeError("Could not open webcam. Check your camera index/permissions.")

print("Camera started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    if now - last_sent >= CAPTURE_INTERVAL_SECONDS:
        last_sent = now
        _, img_encoded = cv2.imencode(".jpg", frame)
        files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
        try:
            response = requests.post(API_URL, files=files, timeout=10)
            data = response.json()
            last_message = data.get("message", "")
            print(last_message)
        except requests.exceptions.RequestException as e:
            last_message = f"Error contacting API: {e}"
            print(last_message)

    # Overlay the latest result on the video feed
    cv2.putText(frame, last_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Attendance Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
