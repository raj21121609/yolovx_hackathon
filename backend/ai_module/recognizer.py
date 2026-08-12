import time
import numpy as np
from scipy.spatial.distance import cosine
from deepface import DeepFace

from .config import (
    MODEL_NAME, DETECTOR_BACKEND, DISTANCE_THRESHOLD,
    MIN_MATCHING_FRAMES, MAX_VERIFICATION_TIME, VERIFICATION_COOLDOWN,
    MIN_FACE_SIZE, MIN_BLUR_THRESHOLD
)
import cv2

class FaceRecognizer:
    def __init__(self):
        self.registered_students = []
        self.state = "IDLE"
        self.current_candidate = None
        self.match_count = 0
        self.verification_start_time = 0
        self.last_verified_student_id = None
        self.last_verified_time = 0
        self.last_distance = None

    def load_students(self, students):
        """
        Expects a list of dictionaries:
        [{'id': str, 'name': str, 'embedding': list[float]}]
        """
        self.registered_students = []
        for s in students:
            if s.get('embedding'):
                self.registered_students.append({
                    'id': str(s['id']),
                    'name': s['name'],
                    'embedding': np.array(s['embedding'])
                })
        self.state = "SCANNING"

    def reset_verification(self):
        self.current_candidate = None
        self.match_count = 0
        self.verification_start_time = 0
        self.last_distance = None

    def _check_quality(self, frame):
        # Blur check
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_val = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_val < MIN_BLUR_THRESHOLD:
            return False, "LOW_QUALITY"
        return True, "OK"

    def process_frame(self, frame):
        """
        Main state machine logic per frame.
        Returns (state, result_dict)
        """
        if self.state == "IDLE":
            return self.state, None

        # 1. Cooldown Check
        if self.last_verified_student_id:
            time_since_verify = time.time() - self.last_verified_time
            if time_since_verify < VERIFICATION_COOLDOWN:
                return "VERIFIED", {
                    "student_id": self.last_verified_student_id,
                    "student_name": self.current_candidate['name'] if self.current_candidate else "Unknown",
                    "distance": self.last_distance,
                    "state": "COOLDOWN",
                    "cooldown_remaining": VERIFICATION_COOLDOWN - time_since_verify
                }
            else:
                self.last_verified_student_id = None
                self.reset_verification()
                self.state = "SCANNING"

        # Timeout Check
        if self.current_candidate:
            if time.time() - self.verification_start_time > MAX_VERIFICATION_TIME:
                self.reset_verification()
                self.state = "SCANNING"

        # 2. Extract Faces using DeepFace to get count and size
        try:
            # We enforce detection to get the exact face bounding boxes
            # We don't align yet, just detect to count.
            # wait, represent does detection AND embedding. We can just use represent to get both if there's only 1 face.
            # But we want to fail fast if there are multiple faces without embedding them all.
            # However, DeepFace.represent returns a list of objects per face.
            # So if we call represent, we get the count of faces automatically.
            # Let's call represent directly to save double-processing.
            results = DeepFace.represent(
                img_path=frame,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=True
            )
        except ValueError:
            # No face detected
            self.reset_verification()
            self.state = "SCANNING"
            return self.state, None
        except Exception as e:
            return "CAMERA_ERROR", str(e)

        num_faces = len(results)
        
        if num_faces == 0:
            self.reset_verification()
            self.state = "SCANNING"
            return self.state, None
            
        if num_faces > 1:
            self.reset_verification()
            self.state = "MULTIPLE_FACES"
            return self.state, None

        self.state = "FACE_DETECTED"

        # Single face detected.
        face_info = results[0]
        w = face_info['facial_area']['w']
        h = face_info['facial_area']['h']

        if w < MIN_FACE_SIZE[0] or h < MIN_FACE_SIZE[1]:
            self.reset_verification()
            self.state = "LOW_QUALITY"
            return self.state, "Face too small"

        # Check blur
        q_ok, _ = self._check_quality(frame)
        if not q_ok:
            self.reset_verification()
            self.state = "LOW_QUALITY"
            return self.state, "Blurry"

        self.state = "RECOGNIZING"
        target_embedding = np.array(face_info["embedding"])

        # Matching
        best_match = None
        min_distance = float('inf')

        for student in self.registered_students:
            dist = cosine(target_embedding, student['embedding'])
            if dist < min_distance:
                min_distance = dist
                best_match = student

        if best_match and min_distance <= DISTANCE_THRESHOLD:
            self.last_distance = min_distance
            
            # Multi-frame verify
            if self.current_candidate and self.current_candidate['id'] == best_match['id']:
                self.match_count += 1
                self.state = "MULTI_FRAME_VERIFY"
            else:
                self.current_candidate = best_match
                self.match_count = 1
                self.verification_start_time = time.time()
                self.state = "MULTI_FRAME_VERIFY"

            if self.match_count >= MIN_MATCHING_FRAMES:
                self.state = "VERIFIED"
                self.last_verified_student_id = self.current_candidate['id']
                self.last_verified_time = time.time()
                
                result_data = {
                    "student_id": self.current_candidate['id'],
                    "student_name": self.current_candidate['name'],
                    "distance": float(min_distance),
                    "state": "VERIFIED",
                    "timestamp": time.time()
                }
                return self.state, result_data
            else:
                result_data = {
                    "student_name": self.current_candidate['name'],
                    "distance": float(min_distance),
                    "match_count": self.match_count,
                    "required": MIN_MATCHING_FRAMES
                }
                return self.state, result_data
        else:
            self.reset_verification()
            self.state = "UNKNOWN"
            return self.state, {"distance": float(min_distance) if min_distance != float('inf') else None}
