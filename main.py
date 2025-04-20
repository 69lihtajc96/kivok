#!/usr/bin/env python3
import cv2
import numpy as np
import time
import subprocess
from collections import deque
import os

# Отключение Qt-бэкенда для OpenCV
os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

# === КОНФИГУРАЦИЯ ===
BLINK_DURATION = 0.5        # Время (сек.) отсутствия лица для активации
MOVEMENT_THRESHOLD = 20     # Порог изменения Y для резких кивков (пиксели)
FRAME_INTERVAL = 0.1        # Интервал обработки кадров (сек.)
HISTORY_SIZE = 4            # Размер истории для сглаживания (около 0.4 сек)
COOLDOWN_DURATION = 0.6     # Время задержки после кивка (сек.)
MAX_MOVEMENT_TIME = 0.8     # Максимальное время для резкого кивка (сек.)
SOUND_FILE = "/usr/share/sounds/freedesktop/stereo/complete.oga"
DEBUG_VISUALS = True        # Показывать кадры для отладки

# === ИНИЦИАЛИЗАЦИЯ ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cap.isOpened():
    print("Ошибка: Не удалось открыть камеру")
    exit()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
if face_cascade.empty():
    print("Ошибка: Не удалось загрузить каскад Haar для лиц")
    exit()

blink_start = None
tracking_active = False
y_history = deque(maxlen=HISTORY_SIZE)  # Хранит y-координаты
time_history = deque(maxlen=HISTORY_SIZE)  # Хранит временные метки
last_action_time = 0  # Время последнего действия

# === ФУНКЦИИ УТИЛИТЫ ===
def send_key(key):
    """Эмулирует нажатие клавиши через wtype (для Wayland)."""
    try:
        subprocess.run(["wtype", "-k", key.lower()], check=True)
        print(f"Нажата клавиша: {key}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка wtype: {e}")

def handle_movement():
    """Анализирует движение головы по истории Y-координат."""
    global last_action_time  # Объявляем global в начале функции
    current_time = time.time()
    if (len(y_history) < HISTORY_SIZE or 
        len(time_history) < HISTORY_SIZE or 
        not tracking_active or 
        current_time - last_action_time < COOLDOWN_DURATION):
        return

    # Проверяем, что движение произошло в пределах MAX_MOVEMENT_TIME
    time_span = time_history[-1] - time_history[0]
    if time_span > MAX_MOVEMENT_TIME:
        return  # Игнорируем медленные движения

    # Вычисляем общее изменение y (последнее - первое)
    total_delta = y_history[-1] - y_history[0]
    print(f"Total Delta: {total_delta:.2f}, History: {list(y_history)}, Time Span: {time_span:.2f}s")

    if abs(total_delta) > MOVEMENT_THRESHOLD:
        key = "down" if total_delta > 0 else "up"
        send_key(key)
        y_history.clear()  # Очистка истории после действия
        time_history.clear()
        last_action_time = current_time

# === ОСНОВНОЙ ЦИКЛ ===
try:
    while cap.isOpened():
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("Ошибка: Не удалось получить кадр")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(200, 200))

        if len(faces) == 0:
            if blink_start is None:
                blink_start = time.time()
            elif time.time() - blink_start >= BLINK_DURATION and not tracking_active:
                subprocess.run(["paplay", SOUND_FILE])
                tracking_active = True
                y_history.clear()
                time_history.clear()
            if DEBUG_VISUALS:
                cv2.imshow("Frame", frame)
            continue

        blink_start = None
        main_face = max(faces, key=lambda f: f[2] * f[3])  # Самое большое лицо
        x, y, w, h = main_face
        # Вычисляем центр лица (Y-координата)
        face_center_y = y + h // 2
        y_history.append(face_center_y)
        time_history.append(time.time())
        handle_movement()

        if DEBUG_VISUALS:
            # Отрисовка прямоугольника вокруг лица
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # Отрисовка центра лица
            cv2.circle(frame, (x + w // 2, face_center_y), 5, (0, 0, 255), -1)
            status = "Tracking: ON" if tracking_active else "Tracking: OFF"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        elapsed = time.time() - start_time
        time.sleep(max(0, FRAME_INTERVAL - elapsed))

finally:
    cap.release()
    cv2.destroyAllWindows()
