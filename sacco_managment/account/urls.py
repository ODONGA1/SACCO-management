from django.urls import path
from account import views
from django.urls import include
from .views import all_credit_cards

app_name = "account"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.account, name="account"),
    path("kyc-reg/", views.kyc_registration, name="kyc-reg"),
    path('credit-cards/', all_credit_cards, name='all-credit-cards'),

    
]
