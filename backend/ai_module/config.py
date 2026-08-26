import os

MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "mtcnn"  # More robust than opencv, especially for glasses

MIN_FACE_SIZE = (80, 80) # (width, height)
MIN_BLUR_THRESHOLD = 2.0 # Lowered to allow standard webcam images

CAMERA_TYPE = os.environ.get('CAMERA_TYPE', 'local')
CAMERA_STREAM_URL = os.environ.get('CAMERA_STREAM_URL', 0)
DISTANCE_THRESHOLD = 0.55  # Relaxed for IP webcam differences
MIN_MATCHING_FRAMES = 2  # Reduced for faster confirmation
MAX_VERIFICATION_TIME = 10.0  # Seconds before resetting attempt
VERIFICATION_COOLDOWN = 10.0  # Seconds before a VERIFIED student can be verified again
PROCESS_FPS = 5  # AI processing rate (frames per second)
