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
    
      # Exchange Rates
    path("rates/", views.exchange_rates, name="exchange-rates"),
    path("api/rates/", views.get_exchange_rates_api, name="exchange-rates-api"),
    
    # Reports
    path("reports/", views.generate_reports, name="generate-reports"),
    
    # API Endpoints
    path("api/wallet/<int:wallet_id>/", views.get_wallet_balance_api, name="wallet-balance-api"),

]