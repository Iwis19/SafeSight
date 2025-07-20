import cv2
import time 
from collections import deque
# from mpu6050 import mpu6050  #no mpu6050 sensor :(
import numpy as np
from datetime import datetime
from upload_service import upload_service
import os
import json

# Constants
BUFFER_SECONDS = 300  #5 minute buffer time
FRAME_RATE = 30
RECORDING_INTERVAL = 15  #save "crash" video every x seconds since we do not have a sensor to properly detect crash
OUTPUT_DIR = "recordings"

#sensor detection constants
#ACCEL_THRESHOLD = 20  #change later 
#SENSOR_ADDRESS = 0x68

#create directory if doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

#cam
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fcc = cv2.VideoWriter_fourcc(*'XVID')

#vid buffer
frame_buffer = deque(maxlen=BUFFER_SECONDS * FRAME_RATE)

#sensor setup 
#sensor = mpu6050(SENSOR_ADDRESS)

#no sensor :(
def detect_crash_sensor():
    # accel = sensor.get_accel_data()
    # total_accel = np.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
    # return total_accel > ACCEL_THRESHOLD
    return False  

#saving video
def save_video_segment():
    
    if len(frame_buffer) == 0:
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_filename = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.avi")
    
    out = cv2.VideoWriter(video_filename, fcc, FRAME_RATE, (width, height))
    
    #write frames from buffer
    for frame in frame_buffer:
        out.write(frame)
    
    out.release()
    print(f"Video saved: {video_filename}")
    return video_filename

#dashcam movement detection logic w/sensor 
def car_is_moving():
    #read from gpio pin, or accelerometer
    #return read_gpio_pin() == HIGH

    #since its a demo, true is assumed
    return True  

#recording logic paired w/ the method above
#while True:
#    if car_is_moving():
#        # Main recording logic here
#        pass
#    else:
#        # Optionally stop/pause recording if car is not moving
#        pass

#collects driving data for urban planners
def collect_driving_data():
    data = {
        #the following values are all placeholders for sensor
        'timestamp': datetime.now().isoformat(),
        'sudden_acceleration_count': 0,  
        'sudden_braking_count': 0,       
        'sharp_turn_count': 0,           
        'note': 'No sensor connected, using placeholder values.'
    }

    #output
    filename = f"driving_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Driving data saved: {filename}")

#local storage (on cam, but since raspberry pi, this part is not functional)

#LOCAL_STORAGE_DIR = "/home/pi/dashcam_videos"  #local storage directory
#MAX_LOCAL_STORAGE_GB = 10  #maximum local storage in GB
#
#def setup_local_storage():
#    if not os.path.exists(LOCAL_STORAGE_DIR):
#        os.makedirs(LOCAL_STORAGE_DIR)
#        print(f"Created local storage directory: {LOCAL_STORAGE_DIR}")
# 
#def save_video_locally(video_path, crash_info):
#    try:
#        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#        local_filename = f"backup_{timestamp}_{crash_info.get('device_id', 'unknown')}.avi"
#        local_path = os.path.join(LOCAL_STORAGE_DIR, local_filename)
#        
#        import shutil
#        shutil.copy2(video_path, local_path)
#        print(f"Video backed up locally: {local_path}")
#         
#        #clean up old files
#         cleanup_old_local_videos()
#         
#     except Exception as e:
#         print(f"Local backup failed: {str(e)}")
# 
##delete old video 
#def cleanup_old_local_videos():
#    try:
#        # Calculate current storage usage
#        total_size = 0
#        video_files = []
#         
#        for filename in os.listdir(LOCAL_STORAGE_DIR):
#            if filename.endswith('.avi'):
#                filepath = os.path.join(LOCAL_STORAGE_DIR, filename)
#                file_size = os.path.getsize(filepath)
#                total_size += file_size
#                video_files.append((filepath, os.path.getmtime(filepath)))
#         
#        #convert to GB
#        total_size_gb = total_size / (1024**3)
#         
#        #if storage > 80% full, delete oldest files
#        if total_size_gb > (MAX_LOCAL_STORAGE_GB * 0.8):
#            video_files.sort(key=lambda x: x[1])
#             
#            #delete oldest files until under 50% capacity
#            for filepath, _ in video_files:
#                if total_size_gb <= (MAX_LOCAL_STORAGE_GB * 0.5):
#                    break
#                 
#                file_size = os.path.getsize(filepath)
#                os.remove(filepath)
#                total_size_gb -= file_size / (1024**3)
#                print(f"Deleted old backup: {filepath}")
#                 
#    except Exception as e:
#        print(f"Local cleanup failed: {str(e)}")
#
##example usage in main loop 
#setup_local_storage()  # Call this once at startup
# 
#if video_filename:
#    upload_service.add_crash_video(video_filename, recording_data)

print("AngelEye is recording --> Press Ctrl+C to exit")
print(f"Recording {BUFFER_SECONDS} seconds of footage, saving every {RECORDING_INTERVAL} seconds")

#big main recording loop
try:
    last_save_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            break

        #buffer
        frame_buffer.append(frame)
        
        #video saving using sensor based detection 
        #if detect_crash_sensor():
        #    print("Crash Detected! --> Saving video!")
        #    video_filename = save_video_segment()
        #    if video_filename:
        #        crash_data = {
        #            'acceleration_threshold': ACCEL_THRESHOLD,
        #            'frame_rate': FRAME_RATE,
        #            'buffer_seconds': BUFFER_SECONDS,
        #            'detection_type': 'sensor'
        #        }
        #        upload_service.add_crash_video(video_filename, crash_data)
        #        print("Crash video uploaded to emergency department!")
        #    frame_buffer.clear()
        #    continue
        
        current_time = time.time()
        
        #save video every x seconds for continuous recording
        if current_time - last_save_time >= RECORDING_INTERVAL:
            video_filename = save_video_segment()
            
            if video_filename:
                #uploading to emergency server
                recording_data = {
                    'recording_interval': RECORDING_INTERVAL,
                    'buffer_seconds': BUFFER_SECONDS,
                    'frame_rate': FRAME_RATE,
                    'timestamp': datetime.now().isoformat(),
                    'detection_type': 'continuous'
                }
                upload_service.add_crash_video(video_filename, recording_data)
                print("Recording uploaded to emergency department")
            
            last_save_time = current_time

        #small delay
        time.sleep(1.0/FRAME_RATE)

except KeyboardInterrupt:
    print("\nExiting, saving final recording")
    save_video_segment()

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Recording stopped")