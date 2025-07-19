import cv2
import time 
from collections import deque
# from mpu6050 import mpu6050  # Uncomment if using MPU6050 sensor
import numpy as np
from datetime import datetime
from upload_service import upload_service
import os

# Constants
BUFFER_SECONDS = 300  # 5 minutes buffer
FRAME_RATE = 30
RECORDING_INTERVAL = 30  # Save video every 30 seconds
OUTPUT_DIR = "recordings"

# Sensor-based detection constants (uncomment if using sensor)
# ACCEL_THRESHOLD = 20  # Change later from testing
# SENSOR_ADDRESS = 0x68

# Create recordings directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Camera setup
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fcc = cv2.VideoWriter_fourcc(*'XVID')

# Frame buffer to hold 5 minutes of footage
frame_buffer = deque(maxlen=BUFFER_SECONDS * FRAME_RATE)

# Sensor setup (uncomment if using MPU6050 sensor)
# sensor = mpu6050(SENSOR_ADDRESS)

def detect_crash_sensor():
    """
    Detect crash using MPU6050 accelerometer sensor
    Uncomment this function and the sensor setup above if using a sensor
    """
    # accel = sensor.get_accel_data()
    # total_accel = np.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
    # return total_accel > ACCEL_THRESHOLD
    return False  # Placeholder - replace with sensor logic

def save_video_segment():
    """Save the current 5-minute buffer as a video file"""
    if len(frame_buffer) == 0:
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_filename = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.avi")
    
    out = cv2.VideoWriter(video_filename, fcc, FRAME_RATE, (width, height))
    
    # Write all frames from buffer
    for frame in frame_buffer:
        out.write(frame)
    
    out.release()
    print(f"Video saved: {video_filename}")
    return video_filename

print("AngelEye Continuous Recorder Running --> Press Ctrl+C to exit")
print(f"Recording {BUFFER_SECONDS} seconds of footage, saving every {RECORDING_INTERVAL} seconds")
print("Note: Sensor-based crash detection is commented out. Uncomment sensor code to enable.")

# Main recording loop
try:
    last_save_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            break

        # Add frame to buffer
        frame_buffer.append(frame)
        
        # SENSOR-BASED CRASH DETECTION (uncomment if using sensor)
        # if detect_crash_sensor():
        #     print("Crash Detected! --> Saving video!")
        #     video_filename = save_video_segment()
        #     if video_filename:
        #         crash_data = {
        #             'acceleration_threshold': ACCEL_THRESHOLD,
        #             'frame_rate': FRAME_RATE,
        #             'buffer_seconds': BUFFER_SECONDS,
        #             'detection_type': 'sensor'
        #         }
        #         upload_service.add_crash_video(video_filename, crash_data)
        #         print("Crash video uploaded to emergency department!")
        #     frame_buffer.clear()
        #     continue
        
        current_time = time.time()
        
        # Save video every RECORDING_INTERVAL seconds (continuous recording mode)
        if current_time - last_save_time >= RECORDING_INTERVAL:
            video_filename = save_video_segment()
            
            if video_filename:
                # Upload to emergency department
                recording_data = {
                    'recording_interval': RECORDING_INTERVAL,
                    'buffer_seconds': BUFFER_SECONDS,
                    'frame_rate': FRAME_RATE,
                    'timestamp': datetime.now().isoformat(),
                    'detection_type': 'continuous'
                }
                upload_service.add_crash_video(video_filename, recording_data)
                print("Recording uploaded to emergency department!")
            
            last_save_time = current_time

        # Small delay to maintain frame rate
        time.sleep(1.0/FRAME_RATE)

except KeyboardInterrupt:
    print("\nExiting - saving final recording...")
    save_video_segment()

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Recording stopped")