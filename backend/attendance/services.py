from django.utils import timezone
from datetime import timedelta
from django.db import transaction, IntegrityError
from .models import AttendanceRecord
from students.models import Student

class AttendanceService:
    @staticmethod
    def record_verified_student(session, student_id, distance, verified_at):
        """
        Records attendance for a verified student if the session is ACTIVE.
        Returns (status_string, message)
        """
        if session.status != session.Status.ACTIVE:
            return "ERROR", "Session is not active"

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return "ERROR", "Student not found"

        # Check for existing record
        if AttendanceRecord.objects.filter(session=session, student=student).exists():
            return "ALREADY_MARKED", "Student is already marked for this session"

        # Determine PRESENT vs LATE
        # Session start time + grace period
        if session.start_time:
            grace_end_time = session.start_time + timedelta(minutes=session.grace_period)
            if verified_at > grace_end_time:
                record_status = AttendanceRecord.Status.LATE
            else:
                record_status = AttendanceRecord.Status.PRESENT
        else:
            record_status = AttendanceRecord.Status.PRESENT

        try:
            # Atomic creation to avoid race conditions
            with transaction.atomic():
                record = AttendanceRecord.objects.create(
                    session=session,
                    student=student,
                    status=record_status,
                    confidence=distance,
                    verified_at=verified_at
                )
            return "SUCCESS", f"Marked {record_status}"
        except IntegrityError:
            # Fallback if unique constraint is violated concurrently
            return "ALREADY_MARKED", "Student is already marked for this session"

    @staticmethod
    def mark_absentees(session):
        """
        Marks all registered students without an attendance record for this session as ABSENT.
        """
        with transaction.atomic():
            # Get all students who have a face embedding registered
            registered_students = Student.objects.exclude(face_embedding__isnull=True)
            
            # Get IDs of students who already have a record for this session
            present_student_ids = AttendanceRecord.objects.filter(session=session).values_list('student_id', flat=True)
            
            # Find absentees
            absentees = registered_students.exclude(id__in=present_student_ids)
            
            # Create ABSENT records
            records_to_create = []
            for student in absentees:
                records_to_create.append(
                    AttendanceRecord(
                        session=session,
                        student=student,
                        status=AttendanceRecord.Status.ABSENT,
                        verified_at=None,
                        confidence=None
                    )
                )
                
            if records_to_create:
                AttendanceRecord.objects.bulk_create(records_to_create, ignore_conflicts=True)
