import uuid
from django.db import models

class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        LATE = 'LATE', 'Late'
        ABSENT = 'ABSENT', 'Absent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('attendance_sessions.AttendanceSession', on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=Status.choices)
    confidence = models.FloatField(null=True, blank=True, help_text="Stores the cosine distance of the recognition match")
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'student'], name='unique_session_student_attendance')
        ]

    def __str__(self):
        return f"{self.student.name} - {self.status} ({self.session.subject})"
