import os
import cv2
import urllib.request
import numpy as np
from scipy.spatial.distance import cosine
from ai_module.embedding import generate_embedding

def run_calibration():
    print("Using existing test_images...")
    
    print("\nExtracting embeddings...")
    try:
        emb_p1_base = generate_embedding("test_images/person1_1.jpg")
        emb_p1_v1 = generate_embedding("test_images/person1_2.jpg")
        emb_p1_v2 = generate_embedding("test_images/person1_3.jpg")
        emb_p2 = generate_embedding("test_images/person2_1.jpg")
    except Exception as e:
        print("Failed to generate embeddings:", e)
        return
        
    same_person_dists = [
        cosine(emb_p1_base, emb_p1_v1),
        cosine(emb_p1_base, emb_p1_v2),
        cosine(emb_p1_v1, emb_p1_v2)
    ]
    
    diff_person_dists = [
        cosine(emb_p1_base, emb_p2),
        cosine(emb_p1_v1, emb_p2),
        cosine(emb_p1_v2, emb_p2)
    ]
    
    print("\n--- Same-Person Distances ---")
    for d in same_person_dists:
        print(f"Distance: {d:.4f}")
    print(f"Min: {min(same_person_dists):.4f}")
    print(f"Max: {max(same_person_dists):.4f}")
    print(f"Avg: {np.mean(same_person_dists):.4f}")

    print("\n--- Different-Person Distances ---")
    for d in diff_person_dists:
        print(f"Distance: {d:.4f}")
    print(f"Min: {min(diff_person_dists):.4f}")
    print(f"Max: {max(diff_person_dists):.4f}")
    print(f"Avg: {np.mean(diff_person_dists):.4f}")
    
    recommended = (max(same_person_dists) + min(diff_person_dists)) / 2
    print(f"\nRecommended Threshold: {recommended:.4f}")

if __name__ == "__main__":
    run_calibration()
