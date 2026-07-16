# Face Recognition Attendance System

Real-time face recognition attendance system using OpenCV + `face_recognition`,
with attendance logged to SQLite (not CSV) — includes duplicate-prevention
(won't mark the same person twice in one day).

## Files
- `database.py` — SQLite schema + helper functions (users, attendance tables)
- `register_face.py` — capture and register a new person's face
- `recognize_attendance.py` — main loop: detect faces, match, mark attendance
- `view_attendance.py` — print today's attendance log

## Setup

### 1. Install Python 3.9–3.11
`face_recognition` / `dlib` can be picky with very new Python versions.
3.9–3.11 is the safest range.

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

**If `dlib` fails to install (common on Windows):**
- Easiest fix: install via conda instead —
  ```bash
  conda install -c conda-forge dlib
  pip install face_recognition opencv-python
  ```
- Or install CMake and Visual Studio Build Tools first (dlib compiles from source on Windows), then retry `pip install dlib`.
- On Mac: `brew install cmake` first if it fails.
- On Linux: `sudo apt install cmake build-essential` first if it fails.

This install step is genuinely the most likely place you'll lose time — budget for it.

## Usage

### Step 1 — Register faces
Run once per person:
```bash
python register_face.py "Your Name"
```
A webcam window opens. Wait for a green box around your face, press **SPACE** to capture, **ESC** to cancel.

### Step 2 — Run attendance
```bash
python recognize_attendance.py
```
Recognized faces get a green box + name, and attendance is auto-marked (once per day per person). Unknown faces show red. Press **q** to quit.

### Step 3 — View today's attendance
```bash
python view_attendance.py
```

## How it works (for interview prep)
1. **Detection**: `face_recognition.face_locations()` finds face bounding boxes in each frame (uses a HOG-based or CNN-based detector under the hood).
2. **Encoding**: Each detected face is converted into a 128-dimensional vector (`face_encodings()`) — a numeric "fingerprint" of facial features.
3. **Matching**: We compute Euclidean distance between the live face's encoding and every stored encoding (`face_distance()`). Smallest distance below `MATCH_THRESHOLD` (0.6) = a match.
4. **Storage**: Encodings are stored as raw bytes (`numpy.tobytes()`) in SQLite and reconstructed with `numpy.frombuffer()` on load.
5. **Attendance logic**: Before marking, we check `has_marked_attendance_today()` so one person can't get marked present multiple times if they linger in frame.

## Known limitations (good to mention proactively in interviews — shows maturity)
- **No liveness detection** — a photo held up to the camera can currently fool it. This is a real security gap in basic face-recognition attendance systems.
- **Lighting sensitivity** — accuracy drops in poor lighting.
- **Threshold tuning** — 0.6 is a reasonable default but not tuned for your specific camera/environment; false positives/negatives are possible.
- **Single-machine only** — SQLite is fine for a demo/single-device use, wouldn't scale to multi-location without moving to Postgres + a proper API layer.

These limitations are exactly what the "Tier 2" upgrades (liveness checks, better thresholding, tests) would address if you have time later.
