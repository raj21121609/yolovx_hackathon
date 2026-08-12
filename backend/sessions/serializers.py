from rest_framework import serializers
from .models import AttendanceSession

class AttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = '__all__'
        read_only_fields = ('id', 'faculty', 'start_time', 'end_time', 'status', 'created_at')

class AttendanceSessionDetailSerializer(serializers.ModelSerializer):
    present_count = serializers.SerializerMethodField()
    late_count = serializers.SerializerMethodField()
    absent_count = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = ['id', 'subject', 'faculty', 'start_time', 'end_time', 'status', 'grace_period', 'created_at', 'present_count', 'late_count', 'absent_count']

    def get_present_count(self, obj):
        return obj.records.filter(status='PRESENT').count()

    def get_late_count(self, obj):
        return obj.records.filter(status='LATE').count()

    def get_absent_count(self, obj):
        return obj.records.filter(status='ABSENT').count()
