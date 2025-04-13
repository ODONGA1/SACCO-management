from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "financial_services"

urlpatterns = [
   # Dashboard
    path("", views.crypto_dashboard, name="crypto-dashboard"),
    path("wallet/<int:wallet_id>/", views.wallet_detail, name="wallet-detail"),
    
    # Transactions
    path("transaction/new/", views.create_transaction, name="create-transaction"),
    path("transaction/history/", views.transaction_history, name="transaction-history"),
    path("transaction/<str:txid>/", views.TransactionDetailView.as_view(), name="transaction-detail"),
    
    # Swap
    path("swap/", views.swap_crypto, name="swap-crypto"),
    
    
]