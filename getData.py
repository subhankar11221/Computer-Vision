import cv2
import requests
import threading
import time
import json

ip = "10.50.151.164"
# ip="192.168.0.3"

last_ts = None
tp = 61
imu_act_freq = 10**9/tp
imu_req_freq = int(imu_act_freq / 400.0)

cap = cv2.VideoCapture(f"http://{ip}:8080/video")
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

acc_text = "ACC not available"
gyro_text = "GYRO not available"

imu_count = 0
imu_hz_real = 0
hz_timer = time.time()

last_imu_time = 0
last_index = 0

def imu_reader():
    global acc_text, gyro_text, imu_freq, last_ts

    while True:
        try:
            r = requests.get(f"http://{ip}:8080/sensors.json", timeout=0.033)
            data = r.json()

            accel = data.get("accel", {}).get("data", [])
            gyro = data.get("gyro", {}).get("data", [])

            ts, (Ax, Ay, Az) = accel[last_index::imu_req_freq]
            (Gx, Gy, Gz) = gyro[last_index::imu_req_freq][1]

        except Exception as e:
            acc_text = "IMU error"
            gyro_text = "IMU error"

        time.sleep(0.01)


threading.Thread(target=imu_reader, daemon=True).start()

while True:
    ret, frame = cap.read()
    if not ret:
        break



cap.release()
cv2.destroyAllWindows()
