from deepface import DeepFace
from .config import MODEL_NAME, DETECTOR_BACKEND

def generate_embedding(img_path):
    """
    Generates embedding for a single validated image.
    Returns the embedding list.
    """
    try:
        result = DeepFace.represent(
            img_path=img_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True
        )
        return result[0]["embedding"]
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")
