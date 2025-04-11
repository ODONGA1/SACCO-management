from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import CryptoWallet, CryptoTransaction, ExchangeRate
from .forms import CryptoTransactionForm
import logging

logger = logging.getLogger(__name__)

@login_required
def crypto_dashboard(request):
    wallets = CryptoWallet.objects.filter(user=request.user, is_active=True)
    transactions = CryptoTransaction.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'financial_services/crypto_dashboard.html', {
        'wallets': wallets,
        'transactions': transactions
    })

@login_required
@transaction.atomic
def create_transaction(request):
    if request.method == 'POST':
        form = CryptoTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                
                # Update wallet balance
                wallet = transaction.wallet
                if transaction.transaction_type in ['BUY', 'TRANSFER']:
                    wallet.balance += transaction.amount
                elif transaction.transaction_type in ['SELL', 'SWAP']:
                    wallet.balance -= transaction.amount
                wallet.save()
                
                return redirect('crypto_dashboard')
            except Exception as e:
                logger.error(f"Transaction failed: {str(e)}")
                form.add_error(None, "Transaction processing failed")
    else:
        form = CryptoTransactionForm(user=request.user)
    
    return render(request, 'financial_services/create_transaction.html', {'form': form})

@login_required
def exchange_rates(request):
    rates = ExchangeRate.objects.filter(expires_at__gte=timezone.now())
    return render(request, 'financial_services/exchange_rates.html', {
        'buy_rates': rates.filter(rate_type='BUY'),
        'sell_rates': rates.filter(rate_type='SELL')
    })

@login_required
def swap_crypto(request):
    # Implement crypto swap logic
    pass

@login_required
def transfer_crypto(request):
    # Implement crypto transfer logic
    pass