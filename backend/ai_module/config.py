MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"  # More accurate than opencv

MIN_FACE_SIZE = (80, 80) # (width, height)
MIN_BLUR_THRESHOLD = 2.0 # Lowered to allow standard webcam images

CAMERA_STREAM_URL = 0  # 0 for default local webcam
DISTANCE_THRESHOLD = 0.4  # Temporary calibration value
MIN_MATCHING_FRAMES = 3  # Frames required to confirm verification
MAX_VERIFICATION_TIME = 10.0  # Seconds before resetting attempt
VERIFICATION_COOLDOWN = 10.0  # Seconds before a VERIFIED student can be verified again
PROCESS_FPS = 3  # AI processing rate (frames per second)
