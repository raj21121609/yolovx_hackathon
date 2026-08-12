import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

if not User.objects.filter(email='faculty@visionattend.com').exists():
    User.objects.create_superuser('faculty', 'faculty@visionattend.com', 'faculty123', name='Admin Faculty', role='faculty')
    print("Faculty user created: faculty@visionattend.com / faculty123")
else:
    print("Faculty user already exists")
