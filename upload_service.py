import requests
import json
import os
import time
from datetime import datetime
import threading
from pathlib import Path

class CrashUploadService:
    ###############################################################

    #change digits in http://xxxxxxxxx:5000 to actual IP address
    #allows the Raspberry Pi to upload videos to your laptop server

    ###############################################################
    def __init__(self, server_url="http://10.24.22.66:5000", api_key=None):
        self.server_url = server_url
        self.api_key = api_key
        self.upload_queue = []
        self.uploading = False
        self.retry_attempts = 3
        self.retry_delay = 5  #seconds
        
    def add_crash_video(self, video_path, crash_data=None):
        """Add a crash video to the upload queue"""
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return False
            
        upload_item = {
            'video_path': video_path,
            'crash_data': crash_data or {},
            'timestamp': datetime.now().isoformat(),
            'attempts': 0
        }
        
        self.upload_queue.append(upload_item)
        print(f"Added crash video to upload queue: {video_path}")
        
        #upload if not already running
        if not self.uploading:
            self.start_upload_thread()
            
        return True
    
    #start upload in background thread
    def start_upload_thread(self):
        self.uploading = True
        upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
        upload_thread.start()
    
    #process queue in the background
    def _upload_worker(self):
        while self.upload_queue:
            upload_item = self.upload_queue[0]
            
            if self._upload_video(upload_item):
                #success
                self.upload_queue.pop(0)
                print(f"Successfully uploaded: {upload_item['video_path']}")
            else:
                #fail
                upload_item['attempts'] += 1
                if upload_item['attempts'] >= self.retry_attempts:
                    print(f"Failed to upload after {self.retry_attempts} attempts: {upload_item['video_path']}")
                    self.upload_queue.pop(0)
                else:
                    #retry
                    self.upload_queue.append(self.upload_queue.pop(0))
                    time.sleep(self.retry_delay)
        
        self.uploading = False
    
    #upload a single vid file
    def _upload_video(self, upload_item):
        try:
            video_path = upload_item['video_path']
            
            #preps file and data
            files = {
                'video': ('crash_video.avi', open(video_path, 'rb'), 'video/x-msvideo')
            }
            
            data = {
                'timestamp': upload_item['timestamp'],
                'crash_data': json.dumps(upload_item['crash_data']),
                'device_id': self._get_device_id()
            }
            
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            #upload to server
            response = requests.post(
                f"{self.server_url}/upload_crash",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Upload successful. Server response: {result}")
                return True
            else:
                print(f"Upload failed. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return False
    
    #unique device identifier
    def _get_device_id(self):
        try:
            #get raspberry pi serial number
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial'):
                        return line.split(':')[1].strip()
        except:
            pass
        
        #use hostname otherwise
        import socket
        return socket.gethostname()

upload_service = CrashUploadService() 