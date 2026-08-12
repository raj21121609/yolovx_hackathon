import os
import time
import urllib.request
import cv2
from scipy.spatial.distance import cosine, euclidean
from ai_module.registration import process_registration_samples
from ai_module.embedding import generate_embedding

def download_sample_images():
    os.makedirs("test_images", exist_ok=True)
    
    person1_url = "https://upload.wikimedia.org/wikipedia/commons/a/a8/Bill_Gates_2017_%28cropped%29.jpg"
    person2_url = "https://upload.wikimedia.org/wikipedia/commons/e/ed/Elon_Musk_Royal_Society.jpg"
    
    req = urllib.request.Request(person1_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open("test_images/base1.jpg", 'wb') as out_file:
        out_file.write(response.read())
        
    req = urllib.request.Request(person2_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open("test_images/person2_1.jpg", 'wb') as out_file:
        out_file.write(response.read())

    img1 = cv2.imread("test_images/base1.jpg")
    for i in range(1, 6):
        shift = i * 2
        h, w = img1.shape[:2]
        var_img = img1[shift:h, shift:w]
        cv2.imwrite(f"test_images/person1_{i}.jpg", var_img)

def run_test():
    print("Downloading sample images...")
    download_sample_images()
    
    person1_images = [os.path.join("test_images", f"person1_{i}.jpg") for i in range(1, 6)]
    person2_image = os.path.join("test_images", "person2_1.jpg")
    
    print("\n--- Starting Registration Test ---")
    start_time = time.time()
    
    success, result = process_registration_samples(person1_images)
    
    registration_time = time.time() - start_time
    
    if success:
        print(f"Success! {result['samples_processed']}/5 samples valid")
        print(f"Embedding dimension: {result['embedding_dimension']}")
        print(f"Registration process took: {registration_time:.2f} seconds")
        
        rep_embedding = result['embedding']
        
        print("\n--- Starting Sanity Similarity Test ---")
        emb1 = generate_embedding(person1_images[0])
        emb2 = generate_embedding(person2_image)
        
        dist_same = cosine(rep_embedding, emb1)
        dist_diff = cosine(rep_embedding, emb2)
        
        print(f"Distance (Same Person - Rep vs Image 1): {dist_same:.4f}")
        print(f"Distance (Different Person - Rep vs Image 2): {dist_diff:.4f}")
        
        if dist_same < dist_diff:
            print("Sanity Test Passed: Same-person distance is lower than different-person distance.")
        else:
            print("Sanity Test Failed: Distances do not make sense.")
            
    else:
        print("Registration Failed:", result)

if __name__ == "__main__":
    run_test()
