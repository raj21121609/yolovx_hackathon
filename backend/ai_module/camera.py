import cv2
import time
from .config import CAMERA_STREAM_URL

class CameraStream:
    def __init__(self, stream_url=None):
        self.stream_url = stream_url if stream_url is not None else CAMERA_STREAM_URL
        self.cap = None
        
    def connect(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.stream_url)
        # Give it a tiny bit of time to warm up
        time.sleep(0.5)
        return self.cap.isOpened()
        
    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            if not self.connect():
                return False, None
                
        ret, frame = self.cap.read()
        if not ret:
            # Try to reconnect once if stream failed
            if self.connect():
                ret, frame = self.cap.read()
                
        return ret, frame
        
    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
