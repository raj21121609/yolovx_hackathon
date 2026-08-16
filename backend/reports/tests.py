from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from sessions.models import AttendanceSession
from students.models import Student
from attendance.models import AttendanceRecord

User = get_user_model()

class ReportsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.faculty1 = User.objects.create_user(username='fac1', email='fac1@test.com', password='pw')
        self.faculty2 = User.objects.create_user(username='fac2', email='fac2@test.com', password='pw')
        
        self.student1 = Student.objects.create(name='Alice', roll_number='001')
        self.student2 = Student.objects.create(name='Bob', roll_number='002')
        self.student3 = Student.objects.create(name='Charlie', roll_number='003')
        
        self.session1 = AttendanceSession.objects.create(subject='Math', faculty=self.faculty1, status='COMPLETED')
        self.session2 = AttendanceSession.objects.create(subject='Physics', faculty=self.faculty2, status='COMPLETED')
        
        # Fac 1: Alice (Present), Bob (Late), Charlie (Absent)
        AttendanceRecord.objects.create(session=self.session1, student=self.student1, status='PRESENT')
        AttendanceRecord.objects.create(session=self.session1, student=self.student2, status='LATE')
        AttendanceRecord.objects.create(session=self.session1, student=self.student3, status='ABSENT')
        
        # Fac 2: Alice (Present)
        AttendanceRecord.objects.create(session=self.session2, student=self.student1, status='PRESENT')

    def test_dashboard_analytics(self):
        self.client.force_authenticate(user=self.faculty1)
        url = reverse('dashboard-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['present_today'], 1)
        self.assertEqual(response.data['late_today'], 1)
        self.assertEqual(response.data['absent_today'], 1)
        self.assertEqual(response.data['average_attendance'], 66.67)

    def test_session_report(self):
        self.client.force_authenticate(user=self.faculty1)
        url = reverse('session-report', kwargs={'pk': self.session1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['attendance_percentage'], 66.67)
        
    def test_session_authorization(self):
        self.client.force_authenticate(user=self.faculty1)
        url = reverse('session-report', kwargs={'pk': self.session2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_analytics(self):
        self.client.force_authenticate(user=self.faculty1)
        url = reverse('student-analytics', kwargs={'pk': self.student1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['present'], 1)
        self.assertEqual(response.data['attendance_percentage'], 100.0)

    def test_csv_export(self):
        self.client.force_authenticate(user=self.faculty1)
        url = reverse('session-export', kwargs={'pk': self.session1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn('Alice', content)
        self.assertIn('PRESENT', content)
        self.assertIn('Charlie', content)
        self.assertIn('ABSENT', content)

    def test_low_attendance(self):
        self.client.force_authenticate(user=self.faculty1)
        with self.settings(LOW_ATTENDANCE_THRESHOLD=75.0):
            url = reverse('low-attendance')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            student_names = [s['student_name'] for s in response.data]
            self.assertIn('Charlie', student_names)
            self.assertNotIn('Alice', student_names)
            self.assertNotIn('Bob', student_names)
