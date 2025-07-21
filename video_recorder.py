import cv2
import numpy as np
from moviepy import VideoFileClip
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter
import os
import time
from datetime import datetime
from typing import List, Optional

class VideoRecorder:
    def __init__(self, output_dir: str, width: int = 640, height: int = 480, fps: int = 10):
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.fps = fps
        
        #ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    #save a list of frames as h264 mp4 vid on moviepy
    def save_video_from_frames(self, frames: List[np.ndarray], filename: Optional[str] = None) -> Optional[str]:
        if not frames:
            print("No frames to save")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"recording_{timestamp}.mp4"
        
        video_path = os.path.join(self.output_dir, filename)
        
        try:
            #create a temporary avi file 
            temp_avi = video_path.replace('.mp4', '_temp.avi')
            
            #write frames to temp avi
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(temp_avi, fourcc, self.fps, (self.width, self.height))
            
            if not out.isOpened():
                print(f"Failed to open temporary video file: {temp_avi}")
                return None
            
            for frame in frames:
                out.write(frame)
            out.release()
            
            #convert avi to mp4 with h264 
            print(f"Converting {temp_avi} to {video_path} with H.264 codec...")
            
            #load avi file 
            video_clip = VideoFileClip(temp_avi)
            
            #write w h264 codec
            video_clip.write_videofile(
                video_path,
                codec='libx264',
                audio=False,
                logger=None
            )
            
            #clean up
            video_clip.close()
            
            #remove temp avi file
            if os.path.exists(temp_avi):
                try:
                    os.remove(temp_avi)
                except PermissionError:
                    import time
                    time.sleep(1)
                    try:
                        os.remove(temp_avi)
                    except PermissionError:
                        print(f"Warning: Could not delete temporary file {temp_avi}")
            
            print(f"Video saved successfully: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"Error saving video: {str(e)}")
            #clean up temp files
            temp_avi = video_path.replace('.mp4', '_temp.avi')
            if os.path.exists(temp_avi):
                try:
                    os.remove(temp_avi)
                except PermissionError:
                    print(f"Warning: Could not delete temporary file {temp_avi}")
            return None 