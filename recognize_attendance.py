"""
recognize_attendance.py
-------------------------
The main attendance loop. Run this after you've registered at least one face.

How it works:
1. Loads all known face encodings from the database
2. Opens the webcam and continuously scans for faces
3. Compares each detected face against known encodings
4. If a match is found AND that person hasn't been marked today,
   logs an attendance record with a timestamp
5. Shows live video with names + attendance status overlaid

Press 'q' to quit.
"""

import cv2
import face_recognition
import numpy as np

from database import init_db, get_all_users, has_marked_attendance_today, mark_attendance

# Distance threshold for face matching.
# Lower = stricter match (fewer false positives, more false negatives).
# 0.6 is the commonly used default for face_recognition's model.
MATCH_THRESHOLD = 0.6


def load_known_faces():
    """
    Pull all registered users from the DB and convert their stored
    bytes back into numpy arrays (the format face_recognition needs).
    """
    users = get_all_users()
    known_ids = []
    known_names = []
    known_encodings = []

    for user in users:
        encoding = np.frombuffer(user["encoding"], dtype=np.float64)
        known_ids.append(user["id"])
        known_names.append(user["name"])
        known_encodings.append(encoding)

    return known_ids, known_names, known_encodings


def run_attendance_system():
    init_db()
    known_ids, known_names, known_encodings = load_known_faces()

    if not known_encodings:
        print("No registered users found. Run register_face.py first.")
        return

    print(f"Loaded {len(known_names)} known face(s): {', '.join(known_names)}")

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("ERROR: Could not access webcam.")
        return

    print("Starting attendance system. Press 'q' to quit.")

    # Keep track of who we've already greeted this session so we don't
    # spam the console every single frame while they're still in view.
    greeted_this_session = set()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Downscale for faster processing, then scale coordinates back up later
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare this face to every known encoding
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = int(np.argmin(distances)) if len(distances) > 0 else -1

            name = "Unknown"
            color = (0, 0, 255)  # red for unknown

            if best_match_index != -1 and distances[best_match_index] < MATCH_THRESHOLD:
                user_id = known_ids[best_match_index]
                name = known_names[best_match_index]
                color = (0, 255, 0)  # green for recognized

                if not has_marked_attendance_today(user_id):
                    mark_attendance(user_id)
                    print(f"✅ Attendance marked for {name}")
                    greeted_this_session.add(name)
                elif name not in greeted_this_session:
                    print(f"ℹ️  {name} already marked present today.")
                    greeted_this_session.add(name)

            # Scale face location back up since we processed a downscaled frame
            top *= 4; right *= 4; bottom *= 4; left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Attendance System - press 'q' to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_attendance_system()
