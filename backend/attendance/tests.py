from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from sessions.models import AttendanceSession
from attendance.models import AttendanceRecord
from attendance.services import AttendanceService
from students.models import Student
from ai_module.processor import get_processor

User = get_user_model()

class AttendanceEngineTests(TestCase):
    def setUp(self):
        self.faculty_a = User.objects.create_user(username='fac_a', email='a@example.com', password='pw')
        self.faculty_b = User.objects.create_user(username='fac_b', email='b@example.com', password='pw')
        
        self.student1 = Student.objects.create(name='Raj', roll_number='1', face_embedding=[0.1]*512)
        self.student2 = Student.objects.create(name='Sim', roll_number='2', face_embedding=[0.2]*512)
        self.student_no_face = Student.objects.create(name='John', roll_number='3') # No face
        
        self.session = AttendanceSession.objects.create(
            subject='Math', 
            faculty=self.faculty_a, 
            grace_period=5
        )

    # Session Lifecycle Tests
    def test_create_session(self):
        self.assertEqual(self.session.status, AttendanceSession.Status.CREATED)

    def test_start_session(self):
        self.session.status = AttendanceSession.Status.ACTIVE
        self.session.start_time = timezone.now()
        self.session.save()
        self.assertEqual(self.session.status, AttendanceSession.Status.ACTIVE)
        
    def test_end_session(self):
        self.session.status = AttendanceSession.Status.ACTIVE
        self.session.save()
        
        AttendanceService.mark_absentees(self.session)
        self.session.status = AttendanceSession.Status.COMPLETED
        self.session.end_time = timezone.now()
        self.session.save()
        
        self.assertEqual(self.session.status, AttendanceSession.Status.COMPLETED)
        
    # Attendance Engine Tests
    def test_verified_during_active_session(self):
        self.session.status = AttendanceSession.Status.ACTIVE
        self.session.start_time = timezone.now()
        self.session.save()
        
        status_str, msg = AttendanceService.record_verified_student(
            self.session, self.student1.id, 0.1, timezone.now()
        )
        self.assertEqual(status_str, "SUCCESS")
        
        record = AttendanceRecord.objects.get(session=self.session, student=self.student1)
        self.assertEqual(record.status, AttendanceRecord.Status.PRESENT)

    def test_verified_after_grace_period(self):
        self.session.status = AttendanceSession.Status.ACTIVE
        self.session.start_time = timezone.now() - timedelta(minutes=6)
        self.session.save()
        
        status_str, msg = AttendanceService.record_verified_student(
            self.session, self.student2.id, 0.1, timezone.now()
        )
        
        record = AttendanceRecord.objects.get(session=self.session, student=self.student2)
        self.assertEqual(record.status, AttendanceRecord.Status.LATE)

    def test_duplicate_verification(self):
        self.session.status = AttendanceSession.Status.ACTIVE
        self.session.start_time = timezone.now()
        self.session.save()
        
        AttendanceService.record_verified_student(self.session, self.student1.id, 0.1, timezone.now())
        status_str, msg = AttendanceService.record_verified_student(self.session, self.student1.id, 0.1, timezone.now())
        
        self.assertEqual(status_str, "ALREADY_MARKED")
        self.assertEqual(AttendanceRecord.objects.filter(student=self.student1).count(), 1)

    def test_verification_inactive_session(self):
        status_str, msg = AttendanceService.record_verified_student(
            self.session, self.student1.id, 0.1, timezone.now()
        )
        self.assertEqual(status_str, "ERROR")
        self.assertEqual(AttendanceRecord.objects.count(), 0)

    def test_end_session_missing_students(self):
        self.session.status = AttendanceSession.Status.ACTIVE
        self.session.start_time = timezone.now()
        self.session.save()
        
        # Mark student1 present
        AttendanceService.record_verified_student(self.session, self.student1.id, 0.1, timezone.now())
        
        # End session
        AttendanceService.mark_absentees(self.session)
        
        self.assertEqual(AttendanceRecord.objects.count(), 2) # Student1 (present), Student2 (absent)
        self.assertEqual(AttendanceRecord.objects.get(student=self.student2).status, AttendanceRecord.Status.ABSENT)
        # student_no_face should not be marked since they don't have embeddings
        self.assertFalse(AttendanceRecord.objects.filter(student=self.student_no_face).exists())

    def test_integration(self):
        # 1. Start Session
        self.session.status = AttendanceSession.Status.ACTIVE
        self.session.start_time = timezone.now()
        self.session.save()
        
        # 2. Simulate VERIFIED Raj
        AttendanceService.record_verified_student(self.session, self.student1.id, 0.14, timezone.now())
        
        # 3. Simulate VERIFIED Raj again
        AttendanceService.record_verified_student(self.session, self.student1.id, 0.12, timezone.now())
        
        # 4. End Session
        AttendanceService.mark_absentees(self.session)
        self.session.status = AttendanceSession.Status.COMPLETED
        self.session.save()
        
        records = AttendanceRecord.objects.filter(session=self.session)
        self.assertEqual(records.count(), 2)
        
        r1 = records.get(student=self.student1)
        self.assertEqual(r1.status, AttendanceRecord.Status.PRESENT)
        
        r2 = records.get(student=self.student2)
        self.assertEqual(r2.status, AttendanceRecord.Status.ABSENT)

from rest_framework.test import APIClient

class AttendanceAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.faculty_a = User.objects.create_user(username='fac_a2', email='a2@example.com', password='pw')
        self.faculty_b = User.objects.create_user(username='fac_b2', email='b2@example.com', password='pw')
        self.session = AttendanceSession.objects.create(
            subject='Science',
            faculty=self.faculty_a
        )

    def test_unauthenticated_request(self):
        response = self.client.get('/api/sessions/')
        self.assertEqual(response.status_code, 401)

    def test_faculty_a_can_access_own_session(self):
        self.client.force_authenticate(user=self.faculty_a)
        response = self.client.get(f'/api/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['subject'], 'Science')

    def test_faculty_b_cannot_access_faculty_a_session(self):
        self.client.force_authenticate(user=self.faculty_b)
        response = self.client.get(f'/api/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, 404)
        
    def test_start_and_end_endpoints(self):
        self.client.force_authenticate(user=self.faculty_a)
        
        # Test Start
        r_start = self.client.post(f'/api/sessions/{self.session.id}/start/')
        self.assertEqual(r_start.status_code, 200)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, AttendanceSession.Status.ACTIVE)
        
        # Test End
        r_end = self.client.post(f'/api/sessions/{self.session.id}/end/')
        self.assertEqual(r_end.status_code, 200)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, AttendanceSession.Status.COMPLETED)

