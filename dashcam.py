import cv2
import time 
from collections import deque
#from mpu6050 import mpu6050  #no mpu6050 sensor :(
import numpy as np
from datetime import datetime
from upload_service import upload_service
from video_recorder import VideoRecorder
import os
import json
import select
import sys

#const
BUFFER_SECONDS = 300  #5 minute buffer time
FRAME_RATE = 10
RECORDING_INTERVAL = 30  #save "crash" video every x seconds to mimic crash

###############################################################

    #change path in "home\pi\recordings" to set video path on the actual dashcam product
    #all videos are saved in here (locally)
OUTPUT_DIR = r"C:\PROJECTS BUNDLE\Computer Science\AngelEye\crash_videos"

###############################################################

#sensor detection constants
#ACCEL_THRESHOLD = 20  #change later 
#SENSOR_ADDRESS = 0x68

#create directory if doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

#cam
cap = cv2.VideoCapture(0)
width = 640
height = 480

#initialize video recorder with MoviePy
video_recorder = VideoRecorder(OUTPUT_DIR, width, height, FRAME_RATE)
print("Using MoviePy with H.264 codec for MP4 format")

#vid buffer
frame_buffer = deque(maxlen=BUFFER_SECONDS * FRAME_RATE)

#sensor setup 
#sensor = mpu6050(SENSOR_ADDRESS)

#no sensor :(
def detect_crash_sensor():
    #accel = sensor.get_accel_data()
    #total_accel = np.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
    #return total_accel > ACCEL_THRESHOLD
    return False  

#saving video
def save_video_segment():
    if len(frame_buffer) == 0:
        return None

    print("Saving video using MoviePy with H.264 codec...")
    #convert deque to list for MoviePy
    frames_list = list(frame_buffer)
    video_path = video_recorder.save_video_from_frames(frames_list)
    
    if video_path:
        print(f"Video saved: {video_path}")
        return video_path
    else:
        print("Failed to save video")
        return None

#dashcam movement detection logic w/sensor 
def car_is_moving():
    #read from gpio pin, or accelerometer
    #return read_gpio_pin() == HIGH

    #since its a demo, true is assumed
    return True  

#recording logic paired w/ the method above
#while True:
#    if car_is_moving():
#        #main recording logic goes here
#        pass
#    else:
#        #stop recording when car stops moving for a long period of time (>= 5mins?)
#        pass


###############################################
#COLLECTING URBAN PLANNING ANALYSIS DATA (FOR OURSELVES)
def init_driver_database():
    try:
        result = business_supabase_service.create_drivers_table()
        if result['success']:
            print("Driver database initialized in business Supabase")
        else:
            print(f"Failed to initialize driver database: {result['error']}")
    except Exception as e:
        print(f"Database initialization error: {str(e)}")


def get_or_create_driver(driver_id):
    try:
        driver = business_supabase_service.get_driver(driver_id)
        if not driver:
            new_driver = {
                'driver_id': driver_id,
                'created_at': datetime.now().isoformat(),
                'total_trips': 0,
                'total_driving_time': 0,
                'event_history': {
                    'sudden_acceleration_count': 0,
                    'sudden_braking_count': 0,
                    'sharp_turn_count': 0
                }
            }
            result = business_supabase_service.create_driver(new_driver)
            if result['success']:
                print(f"Created new driver profile in business Supabase: {driver_id}")
                return result['driver']
            else:
                print(f"Failed to create driver: {result['error']}")
                return None
        return driver
    except Exception as e:
        print(f"Error accessing driver database: {str(e)}")
        return None


def save_driver_data(driver_id, driving_data):
    try:
        session_data = {
            'driver_id': driver_id,
            'device_id': driving_data.get('device_id', 'unknown'),
            'timestamp': driving_data.get('timestamp', datetime.now().isoformat()),
            'speed': driving_data.get('speed', 0),
            'location': driving_data.get('location', 'N/A'),
            'sudden_acceleration_count': driving_data.get('sudden_acceleration_count', 0),
            'sudden_braking_count': driving_data.get('sudden_braking_count', 0),
            'sharp_turn_count': driving_data.get('sharp_turn_count', 0)
        }
        result = business_supabase_service.save_driving_session(session_data)
        if result['success']:
            print(f"Saved driving data to business Supabase for driver: {driver_id}")
            return True
        else:
            print(f"Failed to save driver data: {result['error']}")
            return False
    except Exception as e:
        print(f"Error saving driver data: {str(e)}")
        return False


def get_driver_stats(driver_id):
    try:
        result = business_supabase_service.get_driver_stats(driver_id)
        if result['success']:
            return result['stats']
        else:
            print(f"Failed to get driver stats: {result['error']}")
            return None
    except Exception as e:
        print(f"Error getting driver stats: {str(e)}")
        return None
#URBAN PLANNING DATA ENDS HERE
###############################################


###############################################
#COLLECTING DASHBOARD AND DRIVER ACCESSIBLE DRIVING DATA (FOR CLIENTS)
def collect_driving_data(driver_id="demo_driver_001", device_id="unknown"):
    import random
    #generate random values for demo bc no sensor
    data = {
        'timestamp': datetime.now().isoformat(),
        'driver_id': driver_id,
        'device_id': device_id,
        'speed': round(random.uniform(20, 120), 1),  #random speed between 20 and 120 km/h
        'location': f"{round(random.uniform(37, 38), 6)}, {round(random.uniform(-122, -121), 6)}",  #random lat/lon
        'sudden_acceleration_count': random.randint(0, 5),
        'sudden_braking_count': random.randint(0, 5),
        'sharp_turn_count': random.randint(0, 5),
        'note': 'Randomly generated values for dashboard display.'
    }
    return data
#DASHBOARD AND DRIVER DATA ENDS HERE
###############################################


###############################################

#example use in main loop
# init_driver_database() 
# driving_data = collect_driving_data("driver_001")  #use real driver id here

###############################################


print("AngelEye is recording --> Press Ctrl+C to exit")
print(f"Recording {BUFFER_SECONDS/60.0} minutes of footage, saving every {RECORDING_INTERVAL} seconds")

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

        current_time = time.time()
        #save video every RECORDING_INTERVAL seconds
        if current_time - last_save_time >= RECORDING_INTERVAL:
            video_filename = save_video_segment()
            if video_filename:
                recording_data = {
                    'recording_interval': RECORDING_INTERVAL,
                    'buffer_seconds': BUFFER_SECONDS,
                    'frame_rate': FRAME_RATE,
                    'timestamp': datetime.now().isoformat(),
                    'detection_type': 'continuous'
                }
                success = upload_service.add_crash_video(video_filename, recording_data)
                if success:
                    print("Recording uploaded!")
                else:
                    print("Failed to upload recording.")
            last_save_time = current_time

        #delay to maintain frame rate
        time.sleep(1.0 / FRAME_RATE)

except KeyboardInterrupt:
    print("\nExiting - saving final recording...")
    save_video_segment()

finally:
    cap.release()
    print("Recording stopped")