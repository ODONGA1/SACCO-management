from django.urls import path
from . import views

app_name = "financial_services"

urlpatterns = [
    path("crypto/", views.crypto_dashboard, name="crypto-dashboard"),
    path("crypto/transaction/", views.create_transaction, name="create-transaction"),
    path("crypto/swap/", views.swap_crypto, name="swap-crypto"),
    path("crypto/transfer/", views.transfer_crypto, name="transfer-crypto"),
    path("exchange-rates/", views.exchange_rates, name="exchange-rates"),
 
    # Keep other existing URLs
    path("exchange-rates/", views.exchange_rates, name="exchange-rates"),
]




# from django.urls import path
# from financial_services import views


# app_name = "financial_services"

# urlpatterns = [
    
#     # Exchange
#     path("exchange-rates/", views.exchange_rates, name="exchange-rates"),
#     path("currency-exchange/", views.currency_exchange, name="currency-exchange"),
    
#     # Recipients
#     path("recipients/", views.recipient_list, name="recipient-list"),
#     path("recipients/add/", views.add_recipient, name="add-recipient"),
#     path("recipients/<int:pk>/edit/", views.edit_recipient, name="edit-recipient"),
#     path("recipients/<int:pk>/delete/", views.delete_recipient, name="delete-recipient"),
    
#     # Crypto
#     path("crypto-wallet/", views.crypto_wallet, name="crypto-wallet"),
#     path("buy-crypto/", views.buy_crypto, name="buy-crypto"),
#     path("sell-crypto/", views.sell_crypto, name="sell-crypto"),
    
#     # Deposit
#     path("deposit/", views.initiate_deposit, name="initiate-deposit"),
#     path("deposit/process/", views.process_deposit, name="process-deposit"),
    
#     # Withdrawal
#     path("withdraw/", views.initiate_withdrawal, name="initiate-withdrawal"),
#     path("withdraw/process/", views.process_withdrawal, name="process-withdrawal"),
    
#     # path('dashboard/', views.dashboard, name='dashboard'),

# ]
