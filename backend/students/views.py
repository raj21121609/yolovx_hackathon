import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage

from .models import Student
from .serializers import StudentSerializer
from ai_module.registration import process_registration_samples

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = [IsAuthenticated] # Keep simple for now, can be enabled later

    @action(detail=True, methods=['post'], url_path='register-face')
    def register_face(self, request, pk=None):
        student = self.get_object()
        
        files = request.FILES.getlist('images')
        if not files:
            return Response({"success": False, "error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        saved_paths = []
        for f in files:
            file_name = default_storage.save(f.name, f)
            saved_paths.append(default_storage.path(file_name))
            
        success, result = process_registration_samples(saved_paths)
        
        for path in saved_paths:
            if os.path.exists(path):
                os.remove(path)
                
        if success:
            student.face_embedding = result['embedding']
            student.save()
            return Response({
                "success": True,
                "student_id": student.id,
                "samples_processed": result['samples_processed'],
                "embedding_dimension": result['embedding_dimension']
            })
        else:
            return Response({
                "success": False,
                "error": result
            }, status=status.HTTP_400_BAD_REQUEST)
