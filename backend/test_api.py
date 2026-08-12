import requests
import os

BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("Testing Student Creation...")
    student_data = {
        "name": "Bill Gates",
        "roll_number": "CS-001",
        "department": "Computer Science"
    }
    
    r = requests.post(f"{BASE_URL}/students/", json=student_data)
    if r.status_code == 201:
        student = r.json()
        student_id = student['id']
        print(f"Created student: {student_id}")
    else:
        print("Failed to create student:", r.text)
        # Try getting existing
        r2 = requests.get(f"{BASE_URL}/students/")
        students = r2.json()
        if students:
            student_id = students[0]['id']
            print(f"Using existing student: {student_id}")
        else:
            return

    print("\nTesting Face Registration...")
    files = []
    for i in range(1, 6):
        path = f"test_images/person1_{i}.jpg"
        if os.path.exists(path):
            files.append(('images', (f'person1_{i}.jpg', open(path, 'rb'), 'image/jpeg')))
            
    r = requests.post(f"{BASE_URL}/students/{student_id}/register-face/", files=files)
    print("Response status:", r.status_code)
    print("Response JSON:", r.json())
    
    # Close files
    for f in files:
        f[1][1].close()

if __name__ == "__main__":
    test_api()
