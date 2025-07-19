import cv2
import time 
from collections import deque
from mpu6050 import mpu6050
import numpy as np
from datetime import datetime
from upload_service import upload_service

#const
BUFFER_SECONDS = 10
FRAME_RATE = 30
ACCEL_THRESHOLD = 20 #change later from testing
OUTPUT = lambda: f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"

#camera
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fcc = cv2.VideoWriter_fourcc(*'XVID')

#sensor
sensor = mpu6050(0x68)
frame_buffer = deque(maxlen=BUFFER_SECONDS*FRAME_RATE)

#functions
def detect_crash():
    accel = sensor.get_accel_data()
    total_accel = np.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
    return total_accel > ACCEL_THRESHOLD

print("AngelEye running --> Press Ctrl+C to exit")

#algorithm
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_buffer.append(frame)
        if detect_crash():
            print("Crash Detected! --> Saving video!")
            video_filename = OUTPUT()
            out = cv2.VideoWriter(video_filename, fcc, FRAME_RATE, (width,height))
            for f in frame_buffer:
                out.write(f)
            out.release()
            frame_buffer.clear()
            print("Video outputted!")
            
            # Upload to emergency department
            crash_data = {
                'acceleration_threshold': ACCEL_THRESHOLD,
                'frame_rate': FRAME_RATE,
                'buffer_seconds': BUFFER_SECONDS
            }
            upload_service.add_crash_video(video_filename, crash_data)
            print("Crash video queued for upload to emergency department!\n")

        time.sleep(1.0/FRAME_RATE)

except KeyboardInterrupt:
    print("Exiting")

finally:
    cap.release()
    cv2.destroyAllWindows()