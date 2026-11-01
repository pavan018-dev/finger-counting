# ============================================================
#  Real-Time Finger Counting System — Flask Backend
#  Run : python finger_counter.py
#  Open: http://localhost:5000 in your browser
# ============================================================
import os, math, time, cv2, threading, urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from flask import Flask, Response, jsonify

app = Flask(__name__)
MODEL = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
if not os.path.exists(MODEL):
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, MODEL)

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL),
    num_hands=1, min_hand_detection_confidence=0.6
)
detector = vision.HandLandmarker.create_from_options(options)

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4), (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12), (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20), (0,17)
]
state = {"frame": None, "count": 0, "detected": False, "camera_available": False}
lock  = threading.Lock()

def dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)
def count_fingers(lm):
    # Palm scale reference: distance from wrist (0) to middle MCP (9)
    palm = dist(lm[0], lm[9]) or 0.001
    count = 0
    # Thumb: tip (4) to pinky MCP (17) must be clearly extended beyond thumb IP (3)
    if dist(lm[4], lm[17]) > dist(lm[3], lm[17]) * 1.15:
        count += 1
    # 4 Fingers: tip distance to wrist (0) must exceed PIP distance with margin
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if dist(lm[tip], lm[0]) > dist(lm[pip], lm[0]) + palm * 0.15:
            count += 1
    return count

def capture_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # Hosting services (including Render) do not have access to a visitor's
        # webcam. Keep the web app responsive rather than spinning forever.
        with lock:
            state["camera_available"] = False
        return

    with lock:
        state["camera_available"] = True

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        res = detector.detect(mp_image)

        cnt, det = 0, False
        if res.hand_landmarks:
            det = True
            lms = res.hand_landmarks[0]
            cnt = count_fingers(lms)

            # Draw skeleton connections & landmarks
            for p1, p2 in HAND_CONNECTIONS:
                pt1 = (int(lms[p1].x * w), int(lms[p1].y * h))
                pt2 = (int(lms[p2].x * w), int(lms[p2].y * h))
                cv2.line(frame, pt1, pt2, (255, 255, 255), 2)
            for p in lms:
                cv2.circle(frame, (int(p.x * w), int(p.y * h)), 4, (0, 255, 0), -1)

        with lock:
            state["frame"], state["count"], state["detected"] = frame, cnt, det

def generate_stream():
    while True:
        with lock:
            frame = state["frame"]
        if frame is None: continue
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")

@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return f.read()

@app.route("/video_feed")
def video_feed():
    with lock:
        camera_available = state["camera_available"]
    if not camera_available:
        return ("No server camera is available. Run locally to use webcam detection.", 503)
    return Response(generate_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/count")
def get_count():
    with lock:
        return jsonify(
            count=state["count"],
            detected=state["detected"],
            camera_available=state["camera_available"],
        )

@app.route("/health")
def health():
    return jsonify(status="ok")

# Start capture at import time so production WSGI servers (Gunicorn) work as
# well as `python finger_counter.py`.
threading.Thread(target=capture_loop, daemon=True).start()

if __name__ == "__main__":
    print("[INFO] Server running at http://localhost:5000")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
