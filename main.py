import cv2
import requests
import threading
import time
import json

ip = "10.50.151.164"
# ip="192.168.0.3"

last_ts = None
imu_freq = 0.0

cap = cv2.VideoCapture(f"http://{ip}:8080/video")
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

acc_text = "ACC not available"
gyro_text = "GYRO not available"

imu_count = 0
imu_hz_real = 0
hz_timer = time.time()

last_imu_time = 0

def imu_reader():
    global acc_text, gyro_text, imu_freq, last_ts

    while True:
        try:
            r = requests.get(f"http://{ip}:8080/sensors.json", timeout=0.033)
            data = r.json() 

            accel = data.get("accel", {}).get("data", [])
            gyro = data.get("gyro", {}).get("data", [])
            
            ts, (Ax, Ay, Az) = accel[-1]
            GYRx, GYRy, GYRz = gyro[-1][1]
            last_ts=accel[-2][0]
            print("last_ts",last_ts)

            if last_ts is not None and ts != last_ts:
                dt = ts - last_ts
                print("ts",ts)
                print("dt",dt)
                if dt > 0:
                    imu_freq = 1000/dt

            last_ts = ts

            acc_text = f"ACC X:{Ax:.2f} Y:{Ay:.2f} Z:{Az:.2f}"
            gyro_text = f"GYRO X:{GYRx:.2f} Y:{GYRy:.2f} Z:{GYRz:.2f}"

        except Exception as e:
            acc_text = "IMU error"
            gyro_text = "IMU error"

        time.sleep(0.01)


threading.Thread(target=imu_reader, daemon=True).start()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.putText(frame, acc_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(frame, gyro_text, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(frame, f"IMU Hz: {imu_freq:.1f}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow("Mobile Camera + IMU (Lag Free)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()



