from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
    path('sessions/<uuid:pk>/', views.SessionReportView.as_view(), name='session-report'),
    path('sessions/<uuid:pk>/export/', views.SessionExportView.as_view(), name='session-export'),
    path('students/<uuid:pk>/', views.StudentAnalyticsView.as_view(), name='student-analytics'),
    path('history/', views.AttendanceHistoryView.as_view(), name='attendance-history'),
    path('low-attendance/', views.LowAttendanceView.as_view(), name='low-attendance'),
]
