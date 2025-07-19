from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
CORS(app)

#config
UPLOAD_FOLDER = 'crash_videos'
ALLOWED_EXTENSIONS = {'avi', 'mp4', 'mov', 'mkv'}
DATABASE = 'emergency_crashes.db'

#check upload dir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#initialize sql db
def init_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            video_filename TEXT NOT NULL,
            crash_data TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')

#emergency server dashboard
def dashboard():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, device_id, timestamp, video_filename, crash_data, uploaded_at, status 
        FROM crashes 
        ORDER BY uploaded_at DESC
    ''')
    crashes = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', crashes=crashes)

@app.route('/upload_crash', methods=['POST'])

#receive crash upload from device
def upload_crash():
    try:
        #check if vid is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        #additional data
        timestamp = request.form.get('timestamp', datetime.now().isoformat())
        crash_data = request.form.get('crash_data', '{}')
        device_id = request.form.get('device_id', 'unknown')
        
        #save vid file
        filename = f"crash_{device_id}_{timestamp.replace(':', '-')}.avi"
        filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(filepath)
        
        #store
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO crashes (device_id, timestamp, video_filename, crash_data)
            VALUES (?, ?, ?, ?)
        ''', (device_id, timestamp, filename, crash_data))
        conn.commit()
        conn.close()
        
        print(f"Crash video uploaded: {filename} from device {device_id}")
        
        return jsonify({
            'success': True,
            'message': 'Crash video uploaded successfully',
            'filename': filename,
            'id': cursor.lastrowid
        })
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/video/<filename>')

#serve vid files
def serve_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/crashes')

#api endpoint to see all crashes
def get_crashes():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, device_id, timestamp, video_filename, crash_data, uploaded_at, status 
        FROM crashes 
        ORDER BY uploaded_at DESC
    ''')
    crashes = cursor.fetchall()
    conn.close()
    
    crash_list = []
    for crash in crashes:
        crash_list.append({
            'id': crash[0],
            'device_id': crash[1],
            'timestamp': crash[2],
            'video_filename': crash[3],
            'crash_data': json.loads(crash[4]) if crash[4] else {},
            'uploaded_at': crash[5],
            'status': crash[6]
        })
    
    return jsonify(crash_list)

@app.route('/api/crash/<int:crash_id>/status', methods=['PUT'])

#update crash status (reviewed, urgent, etc)
def update_crash_status(crash_id):
    status = request.json.get('status')
    if not status:
        return jsonify({'error': 'Status required'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE crashes SET status = ? WHERE id = ?', (status, crash_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Status updated'})

if __name__ == '__main__':
    init_database()
    print("Emergency Department Server Starting...")
    print("Dashboard available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 