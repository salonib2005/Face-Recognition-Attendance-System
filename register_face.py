"""
register_face.py
------------------
Run this once per person to register their face.

How it works:
1. Opens your webcam
2. Waits until it detects exactly one face
3. Press SPACE to capture and save that face's encoding to the database
4. Press ESC to cancel

Usage:
    python register_face.py "John Doe"
"""

import sys
import cv2
import face_recognition
import numpy as np

from database import init_db, add_user


def register_face(name: str):
    init_db()  # make sure tables exist before we try to insert

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("ERROR: Could not access webcam. Check camera permissions/index.")
        return

    print(f"Registering face for: {name}")
    print("Look at the camera. Press SPACE to capture, ESC to cancel.")

    captured_encoding = None

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame from webcam.")
            break

        # face_recognition expects RGB, OpenCV gives BGR by default
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)

        # Draw a box around any detected face so the user gets visual feedback
        display_frame = frame.copy()
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)

        status = f"Faces detected: {len(face_locations)}"
        cv2.putText(display_frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Register Face - SPACE to capture, ESC to cancel", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            print("Registration cancelled.")
            break

        if key == 32:  # SPACE
            if len(face_locations) != 1:
                print(f"Need exactly ONE face in frame (found {len(face_locations)}). Try again.")
                continue

            encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            captured_encoding = encodings[0]
            print("Face captured successfully.")
            break

    video_capture.release()
    cv2.destroyAllWindows()

    if captured_encoding is not None:
        # Store the 128-d encoding as raw bytes in SQLite
        encoding_bytes = captured_encoding.astype(np.float64).tobytes()
        try:
            add_user(name, encoding_bytes)
            print(f"✅ '{name}' registered successfully in the database.")
        except Exception as e:
            print(f"❌ Failed to save user (maybe name already exists?): {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python register_face.py "Full Name"')
        sys.exit(1)

    register_face(sys.argv[1])
