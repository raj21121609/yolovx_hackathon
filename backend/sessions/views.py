from django.utils import timezone
from django.http import StreamingHttpResponse
import cv2
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        processor = get_processor()
        
        # Auto-resume orphaned active sessions (e.g., after server restart)
        if instance.status == AttendanceSession.Status.ACTIVE:
            if processor.active_session_id != instance.id and processor.active_session_id is None:
                print(f"Auto-resuming orphaned session {instance.id}")
                processor.start_session(instance)
                
            if processor.active_session_id == instance.id:
                data['stream_token'] = processor.stream_token
            
        return Response(data)

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
        
        stream_token = msg if success else None
            
        serializer = self.get_serializer(session)
        data = serializer.data
        if stream_token:
            data['stream_token'] = stream_token
        return Response(data)

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
        
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def stream(self, request, pk=None):
        from django.shortcuts import get_object_or_404
        session = get_object_or_404(AttendanceSession, pk=pk)
        token = request.query_params.get('token')
        processor = get_processor()
        
        if session.status != AttendanceSession.Status.ACTIVE or processor.active_session_id != session.id:
            return Response({"error": "Session is not active"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not token or token != processor.stream_token:
            return Response({"error": "Invalid or missing stream token"}, status=status.HTTP_403_FORBIDDEN)
            
        def gen_frames():
            import time
            while True:
                with processor.state_lock:
                    frame = processor.latest_frame
                
                if frame is not None:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.05)
                
        return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        session = self.get_object()
        processor = get_processor()
        
        if session.status != AttendanceSession.Status.ACTIVE or processor.active_session_id != session.id:
            return Response({"state": "IDLE", "info": None})
            
        with processor.state_lock:
            state = processor.latest_state
            info = processor.latest_result_info
            
        return Response({
            "state": state,
            "info": info
        })
