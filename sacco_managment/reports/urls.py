from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generate/', views.generate_report, name='generate_report'),
    path('history/', views.report_history, name='report_history'),
    path('download/<int:report_id>/', views.download_report, name='download_report'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
]