#!/usr/bin/env python3
import cv2, numpy as np, time, subprocess, os, logging
from collections import deque

os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

BLINK_DURATION = 0.5
MOVEMENT_THRESHOLD = 20
FRAME_INTERVAL = 0.1
HISTORY_SIZE = 4
COOLDOWN_DURATION = 0.6
MAX_MOVEMENT_TIME = 0.8
SOUND_FILE = "/usr/share/sounds/freedesktop/stereo/complete.oga"
DEBUG_VISUALS = True

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class HeadTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not self.cap.isOpened():
            raise RuntimeError("Camera not available")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if self.face_cascade.empty():
            raise RuntimeError("Haar cascade not loaded")
        self.blink_start = None
        self.tracking_active = False
        self.y_history = deque(maxlen=HISTORY_SIZE)
        self.time_history = deque(maxlen=HISTORY_SIZE)
        self.last_action_time = 0

    def send_key(self, key: str):
        try:
            subprocess.run(["wtype", "-k", key.lower()], check=True)
            logging.info(f"Key pressed: {key}")
        except subprocess.CalledProcessError as e:
            logging.error(f"wtype failed: {e}")

    def play_sound(self):
        try:
            subprocess.Popen(["paplay", SOUND_FILE])
        except Exception as e:
            logging.error(f"Sound failed: {e}")

    def handle_movement(self):
        t = time.time()
        if len(self.y_history) < HISTORY_SIZE or len(self.time_history) < HISTORY_SIZE:
            return
        if not self.tracking_active or t - self.last_action_time < COOLDOWN_DURATION:
            return
        span = self.time_history[-1] - self.time_history[0]
        if span > MAX_MOVEMENT_TIME:
            return
        delta = self.y_history[-1] - self.y_history[0]
        if abs(delta) > MOVEMENT_THRESHOLD:
            self.send_key("down" if delta > 0 else "up")
            self.y_history.clear()
            self.time_history.clear()
            self.last_action_time = t

    def run(self):
        try:
            while self.cap.isOpened():
                start = time.time()
                ret, frame = self.cap.read()
                if not ret:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(200, 200))
                if len(faces) == 0:
                    if self.blink_start is None:
                        self.blink_start = time.time()
                    elif time.time() - self.blink_start >= BLINK_DURATION and not self.tracking_active:
                        self.play_sound()
                        self.tracking_active = True
                        self.y_history.clear()
                        self.time_history.clear()
                    if DEBUG_VISUALS:
                        cv2.imshow("Frame", frame)
                    continue
                self.blink_start = None
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                cy = y + h // 2
                self.y_history.append(cy)
                self.time_history.append(time.time())
                self.handle_movement()
                if DEBUG_VISUALS:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.circle(frame, (x + w // 2, cy), 5, (0, 0, 255), -1)
                    cv2.putText(frame, f"Tracking: {'ON' if self.tracking_active else 'OFF'}",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow("Frame", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                time.sleep(max(0, FRAME_INTERVAL - (time.time() - start)))
        finally:
            self.cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    HeadTracker().run()
