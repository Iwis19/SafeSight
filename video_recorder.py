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
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def save_video_from_frames(self, frames: List[np.ndarray], filename: Optional[str] = None) -> Optional[str]:
        """
        Save a list of frames as an H.264 MP4 video using MoviePy.
        
        Args:
            frames: List of numpy arrays (frames)
            filename: Optional filename, will generate if not provided
            
        Returns:
            Path to the saved video file, or None if failed
        """
        if not frames:
            print("No frames to save")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"recording_{timestamp}.mp4"
        
        video_path = os.path.join(self.output_dir, filename)
        
        try:
            # Create a temporary AVI file first (OpenCV can write this reliably)
            temp_avi = video_path.replace('.mp4', '_temp.avi')
            
            # Write frames to temporary AVI using OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(temp_avi, fourcc, self.fps, (self.width, self.height))
            
            if not out.isOpened():
                print(f"Failed to open temporary video file: {temp_avi}")
                return None
            
            for frame in frames:
                out.write(frame)
            out.release()
            
            # Convert AVI to MP4 with H.264 using MoviePy
            print(f"Converting {temp_avi} to {video_path} with H.264 codec...")
            
            # Load the AVI file with MoviePy
            video_clip = VideoFileClip(temp_avi)
            
            # Write as MP4 with H.264 codec
            video_clip.write_videofile(
                video_path,
                codec='libx264',
                audio=False,
                logger=None
            )
            
            # Clean up
            video_clip.close()
            
            # Remove temporary AVI file with retry logic
            if os.path.exists(temp_avi):
                try:
                    os.remove(temp_avi)
                except PermissionError:
                    # Wait a moment and try again
                    import time
                    time.sleep(1)
                    try:
                        os.remove(temp_avi)
                    except PermissionError:
                        print(f"Warning: Could not delete temporary file {temp_avi}")
                        # Continue anyway, the main video was created successfully
            
            print(f"Video saved successfully: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"Error saving video: {str(e)}")
            # Clean up temporary file if it exists
            temp_avi = video_path.replace('.mp4', '_temp.avi')
            if os.path.exists(temp_avi):
                try:
                    os.remove(temp_avi)
                except PermissionError:
                    print(f"Warning: Could not delete temporary file {temp_avi}")
            return None
    
    def create_test_video(self, duration: int = 5) -> Optional[str]:
        """
        Create a test video with colored frames for testing.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Path to the test video file
        """
        frames = []
        num_frames = duration * self.fps
        
        for i in range(num_frames):
            # Create a frame with changing colors
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame[:, :, 0] = (i * 5) % 255  # Blue channel
            frame[:, :, 1] = (i * 3) % 255  # Green channel
            frame[:, :, 2] = (i * 7) % 255  # Red channel
            
            # Add text
            cv2.putText(frame, f'Test Frame {i}', (50, self.height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            frames.append(frame)
        
        return self.save_video_from_frames(frames, f"test_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4") 