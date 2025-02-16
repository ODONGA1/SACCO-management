


# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from .models import ExchangeRate, Recipient, CryptoWallet, CryptoTransaction, Deposit, Withdrawal
# from account.models import Account
# from core.models import Transaction
# import requests

# # Exchange Views
# @login_required
# def exchange_rates(request):
#     rates = ExchangeRate.objects.all()
#     return render(request, 'financial_services/exchange_rates.html', {'rates': rates})

# @login_required
# def currency_exchange(request):
#     if request.method == 'POST':
#         # Implement exchange logic
#         pass
#     return render(request, 'financial_services/currency_exchange.html')

# # Recipient Views
# @login_required
# def recipient_list(request):
#     recipients = Recipient.objects.filter(user=request.user)
#     return render(request, 'financial_services/recipient_list.html', {'recipients': recipients})

# @login_required
# def add_recipient(request):
#     if request.method == 'POST':
#         # Handle form submission
#         pass
#     return render(request, 'financial_services/add_recipient.html')

# # Crypto Views
# @login_required
# def crypto_wallet(request):
#     wallet, created = CryptoWallet.objects.get_or_create(user=request.user)
#     return render(request, 'financial_services/crypto_wallet.html', {'wallet': wallet})

# @login_required
# def buy_crypto(request):
#     if request.method == 'POST':
#         # Implement crypto purchase logic
#         pass
#     return render(request, 'financial_services/buy_crypto.html')

# # Deposit Views
# @login_required
# def initiate_deposit(request):
#     if request.method == 'POST':
#         # Handle deposit initiation
#         pass
#     return render(request, 'financial_services/initiate_deposit.html')

# # Withdrawal Views
# @login_required
# def initiate_withdrawal(request):
#     if request.method == 'POST':
#         # Handle withdrawal initiation
#         pass
#     return render(request, 'financial_services/initiate_withdrawal.html')

# # API Views
# def update_exchange_rates(request):
#     # Implement exchange rate API integration (e.g., with Fixer.io)
#     pass


# def edit_recipient(request, pk):
#     """Edit an existing recipient's details."""
#     recipient = get_object_or_404(Recipient, pk=pk)  # Fetch recipient or return 404
    
#     if request.method == "POST":
#         form = RecipientForm(request.POST, instance=recipient)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Recipient updated successfully.")
#             return redirect("financial_services:recipient-list")  # Redirect after saving
#     else:
#         form = RecipientForm(instance=recipient)

#     context = {
#         "form": form,
#         "recipient": recipient
#     }
#     return render(request, "financial_services/edit_recipient.html", context)


# def delete_recipient(request, pk):
#     """Delete a recipient from the database."""
#     recipient = get_object_or_404(Recipient, pk=pk)
#     recipient.delete()
#     messages.success(request, "Recipient deleted successfully.")
#     return redirect("financial_services:recipient-list")  # Redirect after deletion


# # In views.py
# @login_required
# def sell_crypto(request):
#     if request.method == 'POST':
#         # Implement the logic for selling crypto
#         pass
#     return render(request, 'financial_services/sell_crypto.html')


# # Process deposit

# @login_required
# def process_deposit(request):
#     if request.method == 'POST':
#         # Implement deposit processing logic
#         pass
#     return render(request, 'financial_services/process_deposit.html')


# @login_required
# def process_withdrawal(request):
#     if request.method == 'POST':
#         # Implement withdrawal processing logic
#         pass
#     return render(request, 'financial_services/process_withdrawal.html')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .models import (
    ExchangeRate, 
    Recipient, 
    CryptoWallet, 
    CryptoTransaction, 
    Deposit, 
    Withdrawal
)
from .forms import (
    RecipientForm,
    CryptoPurchaseForm,
    DepositForm,
    WithdrawalForm
)
from account.models import Account
from core.models import Transaction
import requests
import logging

logger = logging.getLogger(__name__)

# Exchange Views
@login_required
def exchange_rates(request):
    try:
        rates = ExchangeRate.objects.select_related('base_currency').all()
        context = {
            'rates': rates,
            'last_updated': rates.first().last_updated if rates else None
        }
        return render(request, 'financial_services/exchange_rates.html', context)
    except Exception as e:
        logger.error(f"Exchange rates error: {str(e)}")
        messages.error(request, "Could not load exchange rates. Please try again later.")
        return redirect('dashboard')

@login_required
def currency_exchange(request):
    if request.method == 'POST':
        try:
            # Implement proper exchange logic with transaction
            with transaction.atomic():
                # Add conversion logic here
                messages.success(request, "Currency exchange completed successfully")
                return redirect('exchange_rates')
        except Exception as e:
            logger.error(f"Currency exchange error: {str(e)}")
            messages.error(request, "Failed to process currency exchange")
            return redirect('currency_exchange')
    return render(request, 'financial_services/currency_exchange.html')

# Recipient Views
@login_required
def recipient_list(request):
    recipients = Recipient.objects.filter(user=request.user).select_related('user')
    return render(request, 'financial_services/recipient_list.html', {'recipients': recipients})

@login_required
def add_recipient(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                recipient = form.save(commit=False)
                recipient.user = request.user
                recipient.save()
                messages.success(request, "Recipient added successfully")
                return redirect('financial_services:recipient-list')
            except Exception as e:
                logger.error(f"Recipient creation error: {str(e)}")
                messages.error(request, "Failed to save recipient")
        else:
            messages.error(request, "Invalid form data")
    else:
        form = RecipientForm(user=request.user)
    
    return render(request, 'financial_services/add_recipient.html', {'form': form})

@login_required
def edit_recipient(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Recipient updated successfully")
                return redirect('financial_services:recipient-list')
            except Exception as e:
                logger.error(f"Recipient update error: {str(e)}")
                messages.error(request, "Failed to update recipient")
        else:
            messages.error(request, "Invalid form data")
    else:
        form = RecipientForm(instance=recipient, user=request.user)
    
    return render(request, 'financial_services/edit_recipient.html', {
        'form': form,
        'recipient': recipient
    })

@login_required
def delete_recipient(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk, user=request.user)
    try:
        recipient.delete()
        messages.success(request, "Recipient deleted successfully")
    except Exception as e:
        logger.error(f"Recipient deletion error: {str(e)}")
        messages.error(request, "Failed to delete recipient")
    return redirect('financial_services:recipient-list')

# Crypto Views
@login_required
def crypto_wallet(request):
    try:
        wallet = CryptoWallet.objects.get(user=request.user)
    except CryptoWallet.DoesNotExist:
        wallet = CryptoWallet.objects.create(user=request.user)
    
    transactions = CryptoTransaction.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:10]
    
    return render(request, 'financial_services/crypto_wallet.html', {
        'wallet': wallet,
        'transactions': transactions
    })

@login_required
@transaction.atomic
def buy_crypto(request):
    if request.method == 'POST':
        form = CryptoPurchaseForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                crypto_transaction = form.save(commit=False)
                crypto_transaction.user = request.user
                crypto_transaction.transaction_type = 'BUY'
                
                # Process fiat deduction and crypto credit
                account = Account.objects.select_for_update().get(user=request.user)
                if account.account_balance < crypto_transaction.fiat_amount:
                    messages.error(request, "Insufficient funds")
                    return redirect('buy_crypto')
                
                account.account_balance -= crypto_transaction.fiat_amount
                account.save()
                
                # Update crypto wallet
                wallet = CryptoWallet.objects.get(user=request.user)
                setattr(wallet, f"{crypto_transaction.crypto_type.lower()}_balance",
                        getattr(wallet, f"{crypto_transaction.crypto_type.lower()}_balance") 
                        + crypto_transaction.amount)
                wallet.save()
                
                crypto_transaction.save()
                messages.success(request, "Crypto purchase successful")
                return redirect('crypto_wallet')
            except Exception as e:
                logger.error(f"Crypto purchase error: {str(e)}")
                messages.error(request, "Failed to process crypto purchase")
                raise
        else:
            messages.error(request, "Invalid form data")
    else:
        form = CryptoPurchaseForm(user=request.user)
    
    return render(request, 'financial_services/buy_crypto.html', {'form': form})

# Deposit Views
@login_required
def initiate_deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                deposit = form.save(commit=False)
                deposit.user = request.user
                deposit.save()
                
                # Process payment gateway integration here
                messages.success(request, "Deposit initiated successfully")
                return redirect('deposit_history')
            except Exception as e:
                logger.error(f"Deposit initiation error: {str(e)}")
                messages.error(request, "Failed to initiate deposit")
        else:
            messages.error(request, "Invalid form data")
    else:
        form = DepositForm(user=request.user)
    
    return render(request, 'financial_services/initiate_deposit.html', {'form': form})

# Withdrawal Views
@login_required
@transaction.atomic
def initiate_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                withdrawal = form.save(commit=False)
                withdrawal.user = request.user
                
                # Check account balance
                account = Account.objects.select_for_update().get(user=request.user)
                if account.account_balance < withdrawal.amount:
                    messages.error(request, "Insufficient funds")
                    return redirect('initiate_withdrawal')
                
                account.account_balance -= withdrawal.amount
                account.save()
                withdrawal.save()
                
                messages.success(request, "Withdrawal initiated successfully")
                return redirect('withdrawal_history')
            except Exception as e:
                logger.error(f"Withdrawal error: {str(e)}")
                messages.error(request, "Failed to process withdrawal")
        else:
            messages.error(request, "Invalid form data")
    else:
        form = WithdrawalForm(user=request.user)
    
    return render(request, 'financial_services/initiate_withdrawal.html', {'form': form})

# API Views
def update_exchange_rates(request):
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        api_key = settings.EXCHANGE_RATE_API_KEY
        response = requests.get(
            f"https://api.apilayer.com/exchangerates_data/latest?base=USD",
            headers={"apikey": api_key},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        with transaction.atomic():
            for currency, rate in data['rates'].items():
                ExchangeRate.objects.update_or_create(
                    base_currency='USD',
                    target_currency=currency,
                    defaults={'rate': rate}
                )
        return JsonResponse({'status': 'success', 'updated': len(data['rates'])})
    except Exception as e:
        logger.error(f"Exchange rate update failed: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
    
 #sell crypto 

@login_required
def sell_crypto(request):
    if request.method == 'POST':
        # Implement the logic for selling crypto
        pass
    return render(request, 'financial_services/sell_crypto.html')


# Process deposit

@login_required
def process_deposit(request):
    if request.method == 'POST':
        # Implement deposit processing logic
        pass
    return render(request, 'financial_services/process_deposit.html')


@login_required
def process_withdrawal(request):
    if request.method == 'POST':
        # Implement withdrawal processing logic
        pass
    return render(request, 'financial_services/process_withdrawal.html')



# def dashboard(request):
#     return render(request, "account/dashboard.html")