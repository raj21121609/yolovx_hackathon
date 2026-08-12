import numpy as np
from .config import DETECTOR_BACKEND
from .quality import check_image_quality, check_face_detection
from .embedding import generate_embedding

def process_registration_samples(img_paths):
    """
    Takes a list of image paths (e.g. 5 samples).
    Validates them, extracts embeddings, and aggregates into a representative embedding.
    Returns (success_bool, result_data_or_error_msg)
    """
    embeddings = []
    
    for path in img_paths:
        q_ok, q_msg = check_image_quality(path)
        if not q_ok:
            return False, f"Validation failed for {path}: {q_msg}"
            
        f_ok, f_msg = check_face_detection(path, DETECTOR_BACKEND)
        if not f_ok:
            return False, f"Detection failed for {path}: {f_msg}"
            
        try:
            emb = generate_embedding(path)
            embeddings.append(emb)
        except Exception as e:
            return False, f"Embedding generation failed for {path}: {e}"
            
    if not embeddings:
        return False, "No valid embeddings generated."
        
    emb_array = np.array(embeddings)
    mean_embedding = np.mean(emb_array, axis=0)
    
    norm = np.linalg.norm(mean_embedding)
    if norm > 0:
        mean_embedding = mean_embedding / norm
        
    return True, {
        "samples_processed": len(embeddings),
        "embedding_dimension": len(mean_embedding),
        "embedding": mean_embedding.tolist()
    }
