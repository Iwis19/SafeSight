# SafeSight

Crash detection and reporting system that automatically captures and uploads crash footage, serving as an improved dashcam for better road safety. Worked with Raspberry Pi 5.

---

## Key Features

1. **Continuous Buffering**
   - Frames are captured with OpenCV
   - A deque buffer maintains the last 2 minutes of footage
   - Ensures pre-crash footage is preserved
2. **Crash Detection Layer**
   - Designed for MPU6050 accelerometer
   - Threshold-based detection
   - Easy sensor upgrades can be made
3. **Recording**
   - Uses MoviePy with H.264 encoding
   - Saves crash clips at configurable intervals
   - File naming with timestamps
4. **Upload Service**
   - Automatically sends saved footage to Supabase
   - Handles auth and API communication
5. **Dashboard Interface**
   - Built with Flask
   - Displays saved videos
   - Allows monitoring and management of recordings  

---

## Tech Stack
- **Python**
- **Flask** (+ CORS)
- **OpenCV**
- **MoviePy**
- **Supabase**
- NumPy, Requests

---

## Project Structure
```text
SafeSight-master/
├── dashcam.py               # Main dashcam loop (buffer + clip saving)
├── video_recorder.py        # MP4 recording logic (MoviePy)
├── upload_service.py        # Upload logic (Supabase / HTTP)
├── dashboard.py             # Flask dashboard server
├── dbservice.py             # Database / cloud integration utilities
├── dbconfig.py              # DB/cloud config wiring
├── config.py                # App configuration
├── requirements.txt
├── templates/
│   └── dashboard.html
└── static/
    ├── css/dashboard.css
    ├── js/dashboard.js
    └── images/
```

## Lessons Learned
- Designing with heavily constrained hardware
- Managing rolling buffers
- Integrating REST APIs with cloud storage
- How to use Flask
- How to not collapse while debugging under the very short amount of time given

## License
MIT
