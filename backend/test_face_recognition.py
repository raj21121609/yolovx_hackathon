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
                start_ai = time.time()
                current_state, result_info = recognizer.process_frame(frame)
                ai_latency = time.time() - start_ai
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
                if current_state == "VERIFIED":
                    cv2.putText(display_frame, f"VERIFIED: {result_info.get('student_name', 'Unknown')}", (20, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(display_frame, f"Dist: {result_info.get('distance', 0.0):.3f}", (20, 120), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                
                elif current_state == "MULTI_FRAME_VERIFY":
                    name = result_info.get('student_name', 'Unknown')
                    match_count = result_info.get('match_count', 0)
                    required = result_info.get('required', 3)
                    dist = result_info.get('distance', 0.0)
                    cv2.putText(display_frame, f"VERIFYING: {name}", (20, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)
                    cv2.putText(display_frame, f"Verification: {match_count} / {required}", (20, 120), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
                    cv2.putText(display_frame, f"Dist: {dist:.3f}", (20, 160), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
                                
                elif current_state == "COOLDOWN":
                    rem = result_info.get('cooldown_remaining', 0)
                    cv2.putText(display_frame, f"COOLDOWN ({rem:.1f}s)", (20, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                                
                elif current_state == "UNKNOWN":
                    dist = result_info.get('distance')
                    cv2.putText(display_frame, "UNKNOWN", (20, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    if dist is not None:
                        cv2.putText(display_frame, f"Dist: {dist:.3f}", (20, 120), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                                    
            cv2.imshow("VisionAttend Live Feed", display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live_recognition()
