import cv2
import time
from .config import CAMERA_STREAM_URL, CAMERA_TYPE

class CameraStream:
    def __init__(self, stream_url=None, camera_type=None):
        self.stream_url = stream_url if stream_url is not None else CAMERA_STREAM_URL
        self.camera_type = camera_type if camera_type is not None else CAMERA_TYPE
        
        # Ensure local webcam URLs are cast to integers for OpenCV
        if self.camera_type == 'local':
            try:
                self.stream_url = int(self.stream_url)
            except ValueError:
                pass
                
        self.cap = None
        self.last_reconnect_time = 0
        
    def connect(self):
        if self.cap is not None:
            self.cap.release()
            
        self.cap = cv2.VideoCapture(self.stream_url)
        # Give it a tiny bit of time to warm up
        time.sleep(0.5)
        return self.cap.isOpened()
        
    def read_frame(self):
        now = time.time()
        
        if self.cap is None or not self.cap.isOpened():
            # Rate limit reconnection attempts to avoid rapid infinite loops
            if now - self.last_reconnect_time < 3.0:
                return False, None
                
            self.last_reconnect_time = now
            if not self.connect():
                return False, None
                
        ret, frame = self.cap.read()
        if not ret:
            # Drop the connection. Reconnection will be attempted on next call
            # with rate limiting applied
            self.release()
            return False, None
                
        return ret, frame
        
    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
