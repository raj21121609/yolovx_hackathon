import csv
from datetime import datetime
from django.db.models import Count, Q, F
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from sessions.models import AttendanceSession
from students.models import Student
from attendance.models import AttendanceRecord

def get_attendance_percentage(present_count, late_count, total_count):
    if total_count == 0:
        return 0.0
    return round(((present_count + late_count) / total_count) * 100, 2)

class DashboardAnalyticsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        faculty = request.user
        today = timezone.now().date()
        
        # Today's sessions
        today_sessions = AttendanceSession.objects.filter(
            faculty=faculty,
            created_at__date=today
        )
        
        total_students = Student.objects.count()
        
        # Calculate overall attendance for today
        records_today = AttendanceRecord.objects.filter(
            session__faculty=faculty,
            session__created_at__date=today
        )
        
        present = records_today.filter(status='PRESENT').count()
        late = records_today.filter(status='LATE').count()
        absent = records_today.filter(status='ABSENT').count()
        
        total_records = present + late + absent
        avg_attendance = get_attendance_percentage(present, late, total_records)
        
        return Response({
            "today_sessions": today_sessions.count(),
            "total_students": total_students,
            "present_today": present,
            "late_today": late,
            "absent_today": absent,
            "average_attendance": avg_attendance
        })

class SessionReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        session = get_object_or_404(AttendanceSession, pk=pk, faculty=request.user)
        total_students = Student.objects.count()
        
        present = session.records.filter(status='PRESENT').count()
        late = session.records.filter(status='LATE').count()
        absent = session.records.filter(status='ABSENT').count()
        
        total_records = present + late + absent
            
        attendance_percentage = get_attendance_percentage(present, late, total_records)
        
        return Response({
            "session_id": session.id,
            "subject": session.subject,
            "date": session.created_at,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "status": session.status,
            "total_students": total_students,
            "present": present,
            "late": late,
            "absent": absent,
            "attendance_percentage": attendance_percentage
        })

class StudentAnalyticsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        records = AttendanceRecord.objects.filter(
            student=student, 
            session__faculty=request.user
        )
        
        total_sessions = records.count()
        present = records.filter(status='PRESENT').count()
        late = records.filter(status='LATE').count()
        absent = records.filter(status='ABSENT').count()
        
        percentage = get_attendance_percentage(present, late, total_sessions)
        
        return Response({
            "student_id": student.id,
            "total_sessions": total_sessions,
            "present": present,
            "late": late,
            "absent": absent,
            "attendance_percentage": percentage
        })

class AttendanceHistoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        queryset = AttendanceRecord.objects.filter(session__faculty=request.user).select_related('student', 'session')
        
        date = request.query_params.get('date')
        student_id = request.query_params.get('student_id')
        status = request.query_params.get('status')
        
        if date:
            queryset = queryset.filter(session__created_at__date=date)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status)
            
        data = []
        for record in queryset.order_by('-created_at'):
            data.append({
                "id": record.id,
                "student_name": record.student.name,
                "roll_number": record.student.roll_number,
                "subject": record.session.subject,
                "date": record.session.created_at,
                "status": record.status,
            })
            
        return Response(data)

class LowAttendanceView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        threshold = getattr(settings, 'LOW_ATTENDANCE_THRESHOLD', 75.0)
        
        students = Student.objects.all()
        results = []
        
        for student in students:
            records = AttendanceRecord.objects.filter(student=student, session__faculty=request.user)
            total = records.count()
            if total > 0:
                present_late = records.filter(status__in=['PRESENT', 'LATE']).count()
                perc = get_attendance_percentage(present_late, 0, total)
                if perc < threshold:
                    results.append({
                        "student_id": student.id,
                        "student_name": student.name,
                        "roll_number": student.roll_number,
                        "attendance_percentage": perc
                    })
                    
        # Sort lowest first
        results.sort(key=lambda x: x['attendance_percentage'])
        return Response(results)

class SessionExportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        session = get_object_or_404(AttendanceSession, pk=pk, faculty=request.user)
        records = session.records.all().select_related('student')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_{session.subject}_{session.created_at.date()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'Student Name', 'Department', 'Status', 'Verified Time', 'Recognition Distance'])
        
        for record in records:
            verified_time = record.verified_at.strftime('%Y-%m-%d %H:%M:%S') if record.verified_at else ''
            distance = round(record.confidence, 4) if record.confidence is not None else ''
            
            if record.status == 'ABSENT':
                verified_time = ''
                distance = ''
                
            writer.writerow([
                record.student.roll_number,
                record.student.name,
                record.student.department,
                record.status,
                verified_time,
                distance
            ])
            
        return response
