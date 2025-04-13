from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import CryptoWallet, CryptoTransaction
from .forms import TransactionForm
from django.http import HttpResponse
import csv
from io import StringIO

@login_required
def dashboard(request):
    wallets = CryptoWallet.objects.filter(user=request.user)
    transactions = CryptoTransaction.objects.filter(
        wallet__user=request.user
    ).order_by('-timestamp')[:10]
    
    return render(request, 'financial_services/dashboard.html', {
        'wallets': wallets,
        'transactions': transactions
    })

@login_required
@transaction.atomic
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            wallet = transaction.wallet
            
            if transaction.transaction_type == 'DEPOSIT':
                wallet.balance += transaction.amount
            else:  # WITHDRAWAL or TRANSFER
                if wallet.balance < transaction.amount:
                    form.add_error('amount', 'Insufficient balance')
                    return render(request, 'crypto/create_transaction.html', {'form': form})
                wallet.balance -= transaction.amount
            
            wallet.save()
            transaction.status = 'COMPLETED'
            transaction.save()
            
            return redirect('crypto_dashboard')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'financial_services/create_transaction.html', {'form': form})

@login_required
def transaction_history(request):
    transactions = CryptoTransaction.objects.filter(
        wallet__user=request.user
    ).order_by('-timestamp')
    
    return render(request, 'financial_services/transaction_history.html', {
        'transactions': transactions
    })

@login_required
def generate_report(request):
    transactions = CryptoTransaction.objects.filter(
        wallet__user=request.user
    ).order_by('-timestamp')
    
    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="crypto_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Amount', 'Currency', 'Status'])
    
    for tx in transactions:
        writer.writerow([
            tx.timestamp.strftime('%Y-%m-%d %H:%M'),
            tx.get_transaction_type_display(),
            tx.amount,
            tx.wallet.wallet_type,
            tx.get_status_display()
        ])
    
    return response