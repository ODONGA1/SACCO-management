from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='crypto_dashboard'),
    path('transaction/', views.create_transaction, name='create_transaction'),
    path('history/', views.transaction_history, name='transaction_history'),
    path('report/', views.generate_report, name='generate_report'),
]