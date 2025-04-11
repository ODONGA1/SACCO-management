from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "financial_services"

urlpatterns = [
    # Dashboard
    path("crypto/", views.crypto_dashboard, name="crypto-dashboard"),
    path("crypto/wallet/<int:wallet_id>/", views.wallet_detail, name="wallet-detail"),
    
    # Transactions
    path("crypto/transaction/", views.create_transaction, name="create-transaction"),
    path("crypto/swap/", views.swap_crypto, name="swap-crypto"),
    path("crypto/transfer/", views.transfer_crypto, name="transfer-crypto"),
    path("crypto/history/", views.transaction_history, name="transaction-history"),
    path("crypto/transaction/<str:txid>/", views.TransactionDetailView.as_view(), name="transaction-detail"),
    
    # Reports
    path("crypto/reports/", views.generate_reports, name="generate-reports"),
    
    # Exchange Rates
    path("exchange-rates/", views.exchange_rates, name="exchange-rates"),
    path("api/exchange-rates/", views.get_exchange_rates_api, name="get-exchange-rates-api"),
    
    # API Endpoints
    path("api/wallet-balance/<int:wallet_id>/", views.get_wallet_balance_api, name="get-wallet-balance-api"),
]