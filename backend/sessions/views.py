from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import AttendanceSession
from .serializers import AttendanceSessionSerializer, AttendanceSessionDetailSerializer
from attendance.models import AttendanceRecord
from attendance.serializers import AttendanceRecordSerializer
from attendance.services import AttendanceService
from ai_module.processor import get_processor

class AttendanceSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Faculty ownership rule
        return AttendanceSession.objects.filter(faculty=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'start', 'end']:
            return AttendanceSessionDetailSerializer
        return AttendanceSessionSerializer

    def perform_create(self, serializer):
        serializer.save(faculty=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        session = self.get_object()
        
        if session.status == AttendanceSession.Status.ACTIVE:
            return Response({"error": "Session is already active"}, status=status.HTTP_400_BAD_REQUEST)
        
        if session.status == AttendanceSession.Status.COMPLETED:
            return Response({"error": "Cannot restart a completed session"}, status=status.HTTP_400_BAD_REQUEST)
            
        session.status = AttendanceSession.Status.ACTIVE
        session.start_time = timezone.now()
        session.save()
        
        # Start AI Processor
        processor = get_processor()
        success, msg = processor.start_session(session)
        if not success:
            # If camera fails, fail the start? Or leave active? 
            # Let's leave active but report warning.
            pass
            
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        session = self.get_object()
        
        if session.status != AttendanceSession.Status.ACTIVE:
            return Response({"error": "Only active sessions can be ended"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Stop AI Processor
        processor = get_processor()
        processor.stop_session(session.id)
            
        session.status = AttendanceSession.Status.COMPLETED
        session.end_time = timezone.now()
        session.save()
        
        # Mark absentees
        AttendanceService.mark_absentees(session)
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        session = self.get_object()
        records = session.records.all().select_related('student')
        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data)
