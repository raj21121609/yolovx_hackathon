import time
import numpy as np
import cv2
from scipy.spatial.distance import cosine
from deepface import DeepFace

from .config import (
    MODEL_NAME, DETECTOR_BACKEND, DISTANCE_THRESHOLD,
    MIN_MATCHING_FRAMES, MAX_VERIFICATION_TIME, VERIFICATION_COOLDOWN,
    MIN_FACE_SIZE, MIN_BLUR_THRESHOLD
)

class FaceRecognizer:
    def __init__(self):
        self.registered_students = []
        
        # State tracking per candidate
        # student_id -> {'name': str, 'match_count': int, 'verification_start_time': float, 'last_distance': float}
        self.active_candidates = {}
        
        # student_id -> float (time verified)
        self.recently_verified = {}
        
        # Overall state of the system for UI
        self.overall_state = "IDLE"

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
        self.overall_state = "SCANNING"
        self.active_candidates = {}
        self.recently_verified = {}

    def reset_verification(self):
        # We keep this for API compatibility, but usually it's per-candidate now.
        self.active_candidates = {}

    def _check_quality(self, frame):
        # Blur check
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_val = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_val < MIN_BLUR_THRESHOLD:
            return False, "LOW_QUALITY"
        return True, "OK"

    def process_frame(self, frame):
        """
        Detects and tracks multiple faces concurrently.
        Returns (state, result_info) where result_info is a dictionary containing
        details about who is verifying, who is verified, and how many unknown faces.
        """
        if self.overall_state == "IDLE":
            return self.overall_state, None

        now = time.time()

        # 1. Cleanup expired candidates
        expired = [sid for sid, data in self.active_candidates.items() 
                   if now - data['verification_start_time'] > MAX_VERIFICATION_TIME]
        for sid in expired:
            del self.active_candidates[sid]
            
        # Cleanup expired cooldowns
        expired_cooldowns = [sid for sid, t in self.recently_verified.items() 
                             if now - t > VERIFICATION_COOLDOWN]
        for sid in expired_cooldowns:
            del self.recently_verified[sid]

        # Resize frame if it's too large to speed up DeepFace (e.g. IP Webcams are often 1080p)
        process_frame = frame
        scale_factor = 1.0
        max_width = 640
        if frame.shape[1] > max_width:
            scale_factor = max_width / float(frame.shape[1])
            new_height = int(frame.shape[0] * scale_factor)
            process_frame = cv2.resize(frame, (max_width, new_height))
            
        # 2. Extract Faces using DeepFace
        try:
            results = DeepFace.represent(
                img_path=process_frame,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=True
            )
        except ValueError:
            # No face detected
            self.overall_state = "SCANNING"
            return self.overall_state, self._build_result_info()
        except Exception as e:
            self.overall_state = "CAMERA_ERROR"
            return self.overall_state, {"error": str(e)}

        num_faces = len(results)
        
        if num_faces == 0:
            self.overall_state = "SCANNING"
            return self.overall_state, self._build_result_info()

        # Check blur once for the frame
        q_ok, _ = self._check_quality(frame)
        if not q_ok:
            self.overall_state = "LOW_QUALITY"
            return self.overall_state, self._build_result_info(error="Frame too blurry")

        self.overall_state = "RECOGNIZING"
        unknown_count = 0
        
        # Track which IDs we saw in this frame to handle multiple faces matching same student
        seen_student_ids = set()
        
        # Process each face
        for face_info in results:
            w = face_info['facial_area']['w']
            h = face_info['facial_area']['h']
            # Removed size skip logic to ensure IP webcam faces are not filtered out

            target_embedding = np.array(face_info["embedding"])
            
            # Find best match
            best_match = None
            min_distance = float('inf')

            for student in self.registered_students:
                dist = cosine(target_embedding, student['embedding'])
                if dist < min_distance:
                    min_distance = dist
                    best_match = student
                    
            print(f"DEBUG: Face size {w}x{h}. Best match: {best_match['name'] if best_match else 'None'} dist: {min_distance}", flush=True)

            if best_match and min_distance <= DISTANCE_THRESHOLD:
                print(f"DEBUG: Matched {best_match['name']} with distance {min_distance}", flush=True)
                sid = best_match['id']
                
                # Identity collision in same frame: Ignore the second one
                if sid in seen_student_ids:
                    continue
                seen_student_ids.add(sid)
                
                # If they are already in cooldown, ignore
                if sid in self.recently_verified:
                    continue
                    
                # Update candidate tracking
                if sid in self.active_candidates:
                    self.active_candidates[sid]['match_count'] += 1
                    self.active_candidates[sid]['last_distance'] = float(min_distance)
                else:
                    self.active_candidates[sid] = {
                        'name': best_match['name'],
                        'match_count': 1,
                        'verification_start_time': now,
                        'last_distance': float(min_distance)
                    }
            else:
                unknown_count += 1
                
        # 3. Check for verifications and emit VERIFIED events
        verified_this_frame = []
        to_verify = []
        for sid, data in self.active_candidates.items():
            if data['match_count'] >= MIN_MATCHING_FRAMES:
                to_verify.append(sid)
                verified_this_frame.append({
                    "student_id": sid,
                    "student_name": data['name'],
                    "distance": data['last_distance'],
                    "timestamp": now
                })
                
        for sid in to_verify:
            self.recently_verified[sid] = now
            del self.active_candidates[sid]
            
        # If no one is being verified or recently verified, but there are unknown faces, signal UNKNOWN
        if unknown_count > 0 and len(self.active_candidates) == 0 and len(verified_this_frame) == 0:
            self.overall_state = "UNKNOWN"

        return self.overall_state, self._build_result_info(
            verified_events=verified_this_frame,
            unknown_count=unknown_count
        )

    def _build_result_info(self, verified_events=None, unknown_count=0, error=None):
        verifying = []
        for sid, data in self.active_candidates.items():
            verifying.append({
                "student_id": sid,
                "student_name": data['name'],
                "match_count": data['match_count'],
                "required": MIN_MATCHING_FRAMES,
                "distance": data['last_distance']
            })
            
        recently_verified_list = []
        now = time.time()
        for sid, t in self.recently_verified.items():
            sname = "Unknown"
            for s in self.registered_students:
                if s['id'] == sid:
                    sname = s['name']
                    break
            recently_verified_list.append({
                "student_id": sid,
                "student_name": sname,
                "cooldown_remaining": max(0, VERIFICATION_COOLDOWN - (now - t))
            })

        return {
            "state": self.overall_state,
            "verifying": verifying,
            "recently_verified": recently_verified_list,
            "verified_events": verified_events or [],
            "unknown_count": unknown_count,
            "error": error
        }
