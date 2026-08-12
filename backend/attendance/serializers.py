from rest_framework import serializers
from .models import AttendanceRecord

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'student_name', 'student_roll_number', 'status', 'confidence', 'verified_at', 'created_at']
