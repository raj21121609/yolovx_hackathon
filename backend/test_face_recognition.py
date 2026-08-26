import os
import sys
import time
import cv2
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from students.models import Student
from ai_module.camera import CameraStream
from ai_module.recognizer import FaceRecognizer
from ai_module.config import PROCESS_FPS, CAMERA_STREAM_URL

def run_live_recognition():
    print("Initializing Recognizer...")
    recognizer = FaceRecognizer()
    
    # Load students from DB
    students_db = Student.objects.exclude(face_embedding__isnull=True)
    student_list = []
    for s in students_db:
        student_list.append({
            'id': str(s.id),
            'name': s.name,
            'embedding': s.face_embedding
        })
    print(f"Loaded {len(student_list)} registered students from PostgreSQL.")
    recognizer.load_students(student_list)

    print(f"Connecting to camera stream: {CAMERA_STREAM_URL}...")
    camera = CameraStream(CAMERA_STREAM_URL)
    if not camera.connect():
        print("Failed to connect to camera.")
        return
        
    print("Camera connected. Starting live recognition window...")
    print("Press 'q' to quit.")
    
    process_interval = 1.0 / PROCESS_FPS
    last_process_time = 0
    
    # State tracking for drawing
    current_state = "IDLE"
    result_info = None
    
    import threading
    ai_thread = None
    ai_lock = threading.Lock()
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = camera.read_frame()
            if not ret or frame is None:
                print("Failed to read frame. Retrying...")
                time.sleep(0.5)
                continue
                
            frame_count += 1
            now = time.time()
            
            # AI Processing rate limiter
            if (now - last_process_time) >= process_interval:
                if ai_thread is None or not ai_thread.is_alive():
                    latest_frame = frame.copy()
                    
                    def process_worker(f):
                        nonlocal current_state, result_info
                        state, info = recognizer.process_frame(f)
                        with ai_lock:
                            current_state = state
                            result_info = info
                            
                    ai_thread = threading.Thread(target=process_worker, args=(latest_frame,))
                    ai_thread.daemon = True
                    ai_thread.start()
                    last_process_time = now
                
                # Calculate FPS
                elapsed = now - start_time
                cam_fps = frame_count / elapsed
                
                # Draw Info
                # We draw on a copy to keep it responsive, but actually we draw on the live frame
            
            display_frame = frame.copy()
            
            # Overlay info
            cv2.putText(display_frame, f"State: {current_state}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        
            if result_info:
                y_offset = 80
                if result_info.get('verifying'):
                    for v in result_info['verifying']:
                        cv2.putText(display_frame, f"VERIFYING: {v['student_name']} {v['match_count']}/{v['required']}", (20, y_offset), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
                        y_offset += 40
                        
                if result_info.get('recently_verified'):
                    for v in result_info['recently_verified']:
                        cv2.putText(display_frame, f"VERIFIED: {v['student_name']} (CD: {v['cooldown_remaining']:.1f}s)", (20, y_offset), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        y_offset += 40
                        
                if result_info.get('unknown_count', 0) > 0:
                    cv2.putText(display_frame, f"UNKNOWN: {result_info['unknown_count']} face(s)", (20, y_offset), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    y_offset += 40

            cv2.imshow("VisionAttend Live Feed", display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live_recognition()
