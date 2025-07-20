from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from datetime import datetime
from supabase_service import supabase_service

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def dashboard():
    """Insurance company dashboard with Supabase data"""
    crashes = supabase_service.get_crashes()
    return render_template('dashboard.html', crashes=crashes)

@app.route('/upload_crash', methods=['POST'])

#receive crash videos from angeleye dev for insurance claims
def upload_crash():
    try:
        #check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        #save video temporarily
        temp_video_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        video_file.save(temp_video_path)
        
        #get additional data
        timestamp = request.form.get('timestamp', datetime.now().isoformat())
        crash_data = request.form.get('crash_data', '{}')
        device_id = request.form.get('device_id', 'unknown')
        
        #prepare crash data
        crash_info = {
            'device_id': device_id,
            'timestamp': timestamp,
            'crash_data': crash_data,
            'acceleration_threshold': request.form.get('acceleration_threshold', '20'),
            'frame_rate': request.form.get('frame_rate', '30'),
            'buffer_seconds': request.form.get('buffer_seconds', '10')
        }
        
        #upload to Supabase
        result = supabase_service.upload_crash_video(temp_video_path, crash_info)
        
        #clean up temporary file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        
        if result['success']:
            print(f"Crash video uploaded to Supabase for insurance claim: {result['crash_id']}")
            return jsonify({
                'success': True,
                'message': 'Crash video uploaded successfully for insurance processing',
                'crash_id': result['crash_id'],
                'video_url': result['video_url']
            })
        else:
            return jsonify({'error': result['error']}), 500
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/crashes')

#api endpoint to get all crashes
def get_crashes():
    crashes = supabase_service.get_crashes()
    return jsonify(crashes)

@app.route('/api/crash/<int:crash_id>/status', methods=['PUT'])

#update crash status
def update_crash_status(crash_id):
    status = request.json.get('status')
    if not status:
        return jsonify({'error': 'Status required'}), 400
    
    success = supabase_service.update_crash_status(crash_id, status)
    
    if success:
        return jsonify({'success': True, 'message': 'Status updated'})
    else:
        return jsonify({'error': 'Failed to update status'}), 500

@app.route('/api/stats')

#get crash statistics
def get_stats():
    stats = supabase_service.get_crash_stats()
    return jsonify(stats)

if __name__ == '__main__':
    print("Insurance Company Server (Supabase) Starting...")
    print("Dashboard available at: http://localhost:5000")
    print("Make sure to set your Supabase credentials in environment variables!")
    app.run(host='0.0.0.0', port=5000, debug=True) 