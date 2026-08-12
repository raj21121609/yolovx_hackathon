import cv2
from .config import MIN_FACE_SIZE, MIN_BLUR_THRESHOLD
from deepface import DeepFace

def check_image_quality(img_path):
    img = cv2.imread(img_path)
    if img is None:
        return False, "No image found or unreadable"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_val = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur_val < MIN_BLUR_THRESHOLD:
        return False, f"Image quality too low (blurry). Var: {blur_val:.2f}"
        
    return True, "Quality OK"

def check_face_detection(img_path, detector_backend):
    try:
        faces = DeepFace.extract_faces(img_path, detector_backend=detector_backend, enforce_detection=True)
        if len(faces) == 0:
            return False, "No face detected"
        elif len(faces) > 1:
            return False, "Multiple faces detected"
            
        face_area = faces[0]['facial_area']
        w, h = face_area['w'], face_area['h']
        
        if w < MIN_FACE_SIZE[0] or h < MIN_FACE_SIZE[1]:
            return False, f"Face too small ({w}x{h})"
            
        return True, "Face OK"
    except ValueError:
        return False, "No face detected"
    except Exception as e:
        return False, str(e)
