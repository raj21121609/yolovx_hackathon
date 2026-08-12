import json
from django.test.client import Client
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

c = Client()
response = c.post('/api/auth/login/', {'email': 'faculty@visionattend.com', 'password': 'faculty123'})
print("Status Code:", response.status_code)
if response.status_code == 200:
    print("Tokens generated successfully:", "access" in response.json())
else:
    print("Error:", response.content)
