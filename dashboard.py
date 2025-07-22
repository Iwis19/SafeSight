from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
import os
import json
from datetime import datetime
from dbservice import supabase_service

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def dashboard():
    """Insurance company dashboard with Supabase data"""
    crashes = supabase_service.get_crashes()
    print("DEBUG: Retrieved crashes from Supabase:")
    for crash in crashes:
        print(f"  Crash ID: {crash.get('id')}")
        print(f"  Video filename: {crash.get('video_filename')}")
        print(f"  Video URL: {crash.get('video_url')}")
        print(f"  Status: {crash.get('status')}")
        print("  ---")
    
    response = make_response(render_template('dashboard.html', crashes=crashes))
    #cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
        temp_video_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video_file.save(temp_video_path)
        
        #get additional data
        timestamp = request.form.get('timestamp', datetime.now().isoformat())
        crash_data_str = request.form.get('crash_data', '{}')
        device_id = request.form.get('device_id', 'unknown')
        
        #parse crash_data if its a JSON string
        try:
            crash_data = json.loads(crash_data_str) if crash_data_str else {}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in crash_data: {crash_data_str}")
            crash_data = {}
        
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
    response = jsonify(crashes)
    #cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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

@app.route('/api/clear-all-crashes', methods=['POST'])

#clear all from db
def clear_all_crashes():
    try:
        success = supabase_service.clear_all_crashes()
        if success:
            return jsonify({'success': True, 'message': 'All crashes cleared from database'})
        else:
            return jsonify({'error': 'Failed to clear crashes'}), 500
    except Exception as e:
        print(f"Clear crashes error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/crash/<int:crash_id>/delete', methods=['DELETE'])

#delete crash by id - doesnt change crash #
def delete_crash(crash_id):
    try:
        success = supabase_service.delete_crash(crash_id)
        if success:
            return jsonify({'success': True, 'message': f'Crash {crash_id} deleted'})
        else:
            return jsonify({'error': 'Failed to delete crash'}), 500
    except Exception as e:
        print(f"Delete crash error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')

#get crash statistics
def get_stats():
    stats = supabase_service.get_crash_stats()
    return jsonify(stats)

@app.route('/debug/bucket')

#debug endpoint to see supabase bucket
def debug_bucket():
    try:
        from dbconfig import get_supabase_client, VIDEO_BUCKET
        supabase = get_supabase_client()
        
        #list files in bucket
        files = supabase.storage.from_(VIDEO_BUCKET).list()
        
        result = {
            'bucket_name': VIDEO_BUCKET,
            'files': files,
            'file_count': len(files) if files else 0
        }
        
        print(f"DEBUG: Bucket '{VIDEO_BUCKET}' contains {len(files) if files else 0} files:")
        if files:
            for file in files:
                print(f"  - {file.get('name', 'unknown')}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"DEBUG: Error checking bucket: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug/test-video-creation')

#test endpoints 
def test_video_creation():
    try:
        from video_recorder import VideoRecorder
        import os
        
        #vid recorder
        recorder = VideoRecorder('crash_videos', 640, 480, 10)
        
        #test vid creator
        video_path = recorder.create_test_video(duration=5)
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            filename = os.path.basename(video_path)
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': video_path,
                'file_size': file_size,
                'message': f'Test video created: {filename} ({file_size} bytes)'
            })
        else:
            return jsonify({'error': 'Video file was not created'}), 500
            
    except Exception as e:
        print(f"Error creating test video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/video/<filename>')

#serve vids from supabase avoidin cors bad problems
def proxy_video(filename):
    try:
        from dbconfig import get_supabase_client, VIDEO_BUCKET
        from flask import Response
        import requests
        
        supabase = get_supabase_client()
        
        #get vid url
        video_url = supabase.storage.from_(VIDEO_BUCKET).get_public_url(filename)
        if video_url.endswith('?'):
            video_url = video_url[:-1]
        
        #get vid content
        response = requests.get(video_url)
        
        if response.status_code == 200:
            #determine mime type
            if filename.lower().endswith('.mp4'):
                mimetype = 'video/mp4'
            else:
                mimetype = 'video/x-msvideo'
            
            #return w proper headers
            return Response(
                response.content,
                mimetype=mimetype,
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            )
        else:
            return jsonify({'error': f'Failed to fetch video: {response.status_code}'}), 500
            
    except Exception as e:
        print(f"Error proxying video {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/crash_videos/<filename>')

#serve vid files from vid folder
def serve_video(filename):
    from flask import send_from_directory
    import os

    #abs path
    crash_videos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crash_videos')
    return send_from_directory(crash_videos_path, filename)

if __name__ == '__main__':
    print("Insurance Company Server (Supabase) Starting...")
    print("Dashboard available at: http://localhost:5000")
    print("Make sure to set your Supabase credentials in environment variables!")
    app.run(host='0.0.0.0', port=5000, debug=True) 