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


    path('mobile-money/deposit/', views.mobile_money_deposit,
         name='mobile-money-deposit'),
    path('mobile-money/withdrawal/', views.mobile_money_withdrawal,
         name='mobile-money-withdrawal'),
    path('mobile-money/transactions/', views.mobile_money_transactions,
         name='mobile-money-transactions'),
    path('webhook/mobile-money/', views.mobile_money_webhook,
         name='mobile-money-webhook'),

]
