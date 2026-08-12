import threading
import time
from django.utils import timezone
from .camera import CameraStream
from .recognizer import FaceRecognizer
from .config import CAMERA_STREAM_URL, PROCESS_FPS
from attendance.services import AttendanceService
from students.models import Student

class RecognitionManager:
    """
    Process-level manager that tracks active recognition workers.
    Enforces one active attendance session for the MVP.
    """
    _instance = None
    
    def __init__(self):
        self.active_session_id = None
        self.thread = None
        self.stop_event = threading.Event()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def start_session(self, session):
        """Starts the background worker for the given session."""
        if self.active_session_id is not None:
            if self.active_session_id == session.id:
                return True, "Already running"
            else:
                self.stop_session(self.active_session_id)
                
        self.active_session_id = session.id
        self.stop_event.clear()
        
        self.thread = threading.Thread(
            target=self._run_loop,
            args=(session,),
            daemon=True
        )
        self.thread.start()
        return True, "Started"
        
    def stop_session(self, session_id):
        """Stops the background worker."""
        if self.active_session_id == session_id:
            self.stop_event.set()
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)
            self.active_session_id = None
            self.thread = None
            return True
        return False
        
    def _run_loop(self, session):
        print(f"AI Processor starting for session: {session.id}")
        
        # Load students
        recognizer = FaceRecognizer()
        students_db = Student.objects.exclude(face_embedding__isnull=True)
        student_list = []
        for s in students_db:
            student_list.append({
                'id': str(s.id),
                'name': s.name,
                'embedding': s.face_embedding
            })
        recognizer.load_students(student_list)
        
        # Connect camera
        camera = CameraStream(CAMERA_STREAM_URL)
        if not camera.connect():
            print("Failed to connect camera.")
            return
            
        process_interval = 1.0 / PROCESS_FPS
        last_process_time = 0
        
        try:
            while not self.stop_event.is_set():
                # Re-check session status periodically to auto-terminate
                session.refresh_from_db()
                if session.status != session.Status.ACTIVE:
                    print("Session is no longer ACTIVE. Terminating AI loop.")
                    break
                    
                ret, frame = camera.read_frame()
                if not ret or frame is None:
                    time.sleep(0.5)
                    continue
                    
                now = time.time()
                if (now - last_process_time) >= process_interval:
                    state, result_info = recognizer.process_frame(frame)
                    last_process_time = now
                    
                    if state == "VERIFIED" and result_info:
                        # Call attendance service
                        student_id = result_info['student_id']
                        distance = result_info['distance']
                        # We use timezone.now() for the DB record time
                        status_str, msg = AttendanceService.record_verified_student(
                            session=session,
                            student_id=student_id,
                            distance=distance,
                            verified_at=timezone.now()
                        )
                        print(f"Verification event processed: {status_str} - {msg}")
                        
        except Exception as e:
            print(f"Error in AI Processor loop: {e}")
        finally:
            camera.release()
            if self.active_session_id == session.id:
                self.active_session_id = None
            print(f"AI Processor stopped for session: {session.id}")

def get_processor():
    return RecognitionManager.get_instance()
