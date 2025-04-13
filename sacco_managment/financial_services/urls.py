from django.urls import path
from . import views


app_name = 'financial_services' 

urlpatterns = [
    
    path('', views.dashboard, name='crypto_dashboard'),
    path('transaction/', views.create_transaction, name='create_transaction'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('report/', views.generate_report, name='generate_report'),
]