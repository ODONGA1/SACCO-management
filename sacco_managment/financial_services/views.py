from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from .models import CryptoWallet, CryptoTransaction, ExchangeRate, CryptoSwap
from .forms import CryptoTransactionForm, CryptoSwapForm, CryptoTransferForm
import logging
from decimal import Decimal
import csv
from datetime import datetime
from io import StringIO
import shortuuid



logger = logging.getLogger(__name__)

@login_required
def crypto_dashboard(request):
    wallets = CryptoWallet.objects.filter(
        user=request.user, 
        is_active=True
    ).select_related('user').prefetch_related('transactions')
    
    transactions = CryptoTransaction.objects.filter(
        user=request.user
    ).select_related('wallet').order_by('-timestamp')[:15]
    
    context = {
        'wallets': wallets,
        'transactions': transactions,
        'total_balance': sum(w.balance for w in wallets)
    }
    return render(request, 'financial_services/crypto_dashboard.html', context)

@login_required
@transaction.atomic
def create_transaction(request):
    if request.method == 'POST':
        form = CryptoTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                crypto_transaction = form.save(commit=False)
                crypto_transaction.user = request.user
                
                # Process transaction based on type
                wallet = crypto_transaction.wallet
                if crypto_transaction.transaction_type in ['BUY', 'TRANSFER_IN']:
                    wallet.balance += crypto_transaction.amount
                elif crypto_transaction.transaction_type in ['SELL', 'SWAP', 'TRANSFER_OUT']:
                    wallet.balance -= (crypto_transaction.amount + crypto_transaction.network_fee)
                
                # Save both objects in transaction
                wallet.save()
                crypto_transaction.save()
                
                messages.success(request, 
                    f"Transaction {crypto_transaction.txid} created successfully!"
                )
                return redirect('financial_services:crypto-dashboard')
                
            except Exception as e:
                logger.error(f"Transaction failed: {str(e)}", exc_info=True)
                messages.error(request, "Transaction processing failed. Please try again.")
    else:
        form = CryptoTransactionForm(user=request.user)
    
    return render(request, 'financial_services/create_transaction.html', {'form': form})

@login_required
def exchange_rates(request):
    now = timezone.now()
    rates = ExchangeRate.objects.filter(
        expires_at__gte=now
    ).order_by('base_currency', 'target_currency', '-effective_date').distinct(
        'base_currency', 'target_currency'
    )
    
    # Group by rate type for display
    rate_groups = {
        'buy': rates.filter(rate_type='BUY'),
        'sell': rates.filter(rate_type='SELL'),
        'mid': rates.filter(rate_type='MID'),
    }
    
    return render(request, 'financial_services/exchange_rates.html', {
        'rate_groups': rate_groups,
        'last_updated': now
    })

@login_required
def wallet_detail(request, wallet_id):
    wallet = get_object_or_404(CryptoWallet, id=wallet_id, user=request.user)
    transactions = wallet.transactions.all().order_by('-timestamp')
    
    return render(request, 'financial_services/wallet_detail.html', {
        'wallet': wallet,
        'transactions': transactions
    })

@login_required
def get_exchange_rates_api(request):
    """API endpoint for AJAX requests to get current exchange rates"""
    rates = ExchangeRate.objects.filter(
        expires_at__gte=timezone.now()
    ).values('base_currency', 'target_currency', 'rate_type', 'rate')
    
    return JsonResponse(list(rates), safe=False)


@login_required
@transaction.atomic
def swap_crypto(request):
    if request.method == 'POST':
        form = CryptoSwapForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                source_wallet = form.cleaned_data['source_wallet']
                target_currency = form.cleaned_data['target_currency']
                amount = form.cleaned_data['amount']
                
                # Get exchange rate
                rate = ExchangeRate.objects.filter(
                    base_currency=source_wallet.wallet_type,
                    target_currency=target_currency,
                    rate_type='MID',
                    expires_at__gte=timezone.now()
                ).first()
                
                if not rate:
                    messages.error(request, "No exchange rate available for this pair")
                    return redirect('financial_services:swap-crypto')
                
                # Calculate amounts with 0.5% swap fee
                swap_fee = Decimal('0.005')  # 0.5%
                fee_amount = amount * swap_fee
                net_amount = amount - fee_amount
                target_amount = net_amount * rate.rate
                
                # Get or create target wallet
                target_wallet, created = CryptoWallet.objects.get_or_create(
                    user=request.user,
                    wallet_type=target_currency,
                    defaults={
                        'address': f"{request.user.id}_{target_currency}_{shortuuid.uuid()}",
                        'balance': 0
                    }
                )
                
                # Create debit transaction
                debit_tx = CryptoTransaction.objects.create(
                    user=request.user,
                    wallet=source_wallet,
                    transaction_type='SWAP_OUT',
                    amount=amount,
                    network_fee=fee_amount,
                    status='CONFIRMED',
                    metadata={
                        'swap_type': 'OUT',
                        'target_currency': target_currency,
                        'exchange_rate': float(rate.rate),
                        'target_amount': float(target_amount)
                    }
                )
                
                # Create credit transaction
                credit_tx = CryptoTransaction.objects.create(
                    user=request.user,
                    wallet=target_wallet,
                    transaction_type='SWAP_IN',
                    amount=target_amount,
                    status='CONFIRMED',
                    metadata={
                        'swap_type': 'IN',
                        'source_currency': source_wallet.wallet_type,
                        'exchange_rate': float(rate.rate),
                        'source_amount': float(amount)
                    }
                )
                
                # Create swap record
                CryptoSwap.objects.create(
                    user=request.user,
                    source_transaction=debit_tx,
                    target_transaction=credit_tx,
                    exchange_rate=rate.rate,
                    swap_fee=fee_amount
                )
                
                # Update balances
                source_wallet.balance -= amount
                target_wallet.balance += target_amount
                source_wallet.save()
                target_wallet.save()
                
                messages.success(request, 
                    f"Successfully swapped {amount:.8f} {source_wallet.wallet_type} to {target_amount:.8f} {target_currency}"
                )
                return redirect('financial_services:crypto-dashboard')
                
            except Exception as e:
                logger.error(f"Swap failed: {str(e)}", exc_info=True)
                messages.error(request, "Swap processing failed. Please try again.")
    else:
        form = CryptoSwapForm(user=request.user)
    
    return render(request, 'financial_services/swap_crypto.html', {
        'form': form,
        'swap_fee': Decimal('0.5')  # 0.5%
    })

@login_required
@transaction.atomic
def transfer_crypto(request):
    if request.method == 'POST':
        form = CryptoTransferForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                wallet = form.cleaned_data['wallet']
                amount = form.cleaned_data['amount']
                recipient_address = form.cleaned_data['recipient_address']
                network_fee = form.cleaned_data.get('network_fee', Decimal('0'))
                
                # Create transaction
                tx = CryptoTransaction.objects.create(
                    user=request.user,
                    wallet=wallet,
                    transaction_type='TRANSFER_OUT',
                    amount=amount,
                    network_fee=network_fee,
                    status='PENDING',  # Would be updated when blockchain confirms
                    metadata={
                        'recipient_address': recipient_address,
                        'network': wallet.wallet_type
                    }
                )
                
                # Update balance (immediate deduction for pending transfer)
                wallet.balance -= (amount + network_fee)
                wallet.save()
                
                # In a real implementation, you would:
                # 1. Broadcast the transaction to the network
                # 2. Update status when confirmation is received
                # 3. Store the transaction hash
                
                # For demo purposes, we'll simulate a successful transfer
                tx.tx_hash = f"0x{''.join([str(i) for i in range(10)])}{''.join([chr(97+i) for i in range(6)])}"
                tx.status = 'CONFIRMED'
                tx.save()
                
                messages.success(request, 
                    f"Transfer of {amount:.8f} {wallet.wallet_type} to {recipient_address[:6]}...{recipient_address[-4:]} completed"
                )
                return redirect('financial_services:crypto-dashboard')
                
            except Exception as e:
                logger.error(f"Transfer failed: {str(e)}", exc_info=True)
                messages.error(request, "Transfer processing failed. Please try again.")
    else:
        form = CryptoTransferForm(user=request.user)
    
    return render(request, 'financial_services/transfer_crypto.html', {
        'form': form,
        'default_fee': Decimal('0.0005')  # Default network fee
    })

@login_required
def transaction_history(request):
    transactions = CryptoTransaction.objects.filter(
        user=request.user
    ).select_related('wallet').order_by('-timestamp')
    
    # Filtering
    wallet_filter = request.GET.get('wallet')
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if wallet_filter:
        transactions = transactions.filter(wallet_id=wallet_filter)
    if type_filter:
        transactions = transactions.filter(transaction_type=type_filter)
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    if date_from:
        transactions = transactions.filter(timestamp__gte=date_from)
    if date_to:
        transactions = transactions.filter(timestamp__lte=date_to)
    
    wallets = CryptoWallet.objects.filter(user=request.user, is_active=True)
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(transactions, 25)  # Show 25 transactions per page
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'financial_services/transaction_history.html', {
        'page_obj': page_obj,
        'wallets': wallets,
        'wallet_filter': wallet_filter,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    })

@login_required
def generate_reports(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        wallet_id = request.POST.get('wallet')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        # Create base queryset
        transactions = CryptoTransaction.objects.filter(
            user=request.user,
            timestamp__gte=date_from,
            timestamp__lte=date_to
        )
        
        if wallet_id:
            transactions = transactions.filter(wallet_id=wallet_id)
        
        transactions = transactions.select_related('wallet').order_by('timestamp')
        
        if report_type == 'csv':
            # Generate CSV report
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="crypto_report_{datetime.now().date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'Date', 'Transaction ID', 'Type', 'Wallet', 'Amount', 
                'Currency', 'Fee', 'Status', 'Hash'
            ])
            
            for tx in transactions:
                writer.writerow([
                    tx.timestamp.strftime('%Y-%m-%d %H:%M'),
                    tx.txid,
                    tx.get_transaction_type_display(),
                    tx.wallet.get_wallet_type_display(),
                    tx.amount,
                    tx.wallet.wallet_type,
                    tx.network_fee,
                    tx.get_status_display(),
                    tx.tx_hash or ''
                ])
            
            return response
        
        elif report_type == 'pdf':
            # In a real implementation, you would use a library like ReportLab
            # or WeasyPrint to generate PDF reports
            # This is a simplified version that returns a text response
            buffer = StringIO()
            buffer.write(f"Cryptocurrency Transaction Report\n")
            buffer.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            buffer.write(f"Date Range: {date_from} to {date_to}\n\n")
            
            for tx in transactions:
                buffer.write(
                    f"{tx.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                    f"{tx.txid} | "
                    f"{tx.get_transaction_type_display():<12} | "
                    f"{tx.wallet.get_wallet_type_display():<10} | "
                    f"{tx.amount:>12.8f} {tx.wallet.wallet_type} | "
                    f"{tx.get_status_display()}\n"
                )
            
            response = HttpResponse(buffer.getvalue(), content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="crypto_report_{datetime.now().date()}.txt"'
            return response
    
    # GET request - show form
    wallets = CryptoWallet.objects.filter(user=request.user, is_active=True)
    default_date_from = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d')
    default_date_to = timezone.now().strftime('%Y-%m-%d')
    
    return render(request, 'financial_services/generate_reports.html', {
        'wallets': wallets,
        'default_date_from': default_date_from,
        'default_date_to': default_date_to
    })

class TransactionDetailView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, txid):
        transaction = get_object_or_404(
            CryptoTransaction, 
            txid=txid, 
            user=request.user
        )
        
        related_transaction = None
        if 'related_transaction' in transaction.metadata:
            related_transaction = CryptoTransaction.objects.filter(
                txid=transaction.metadata['related_transaction']
            ).first()
        
        return render(request, 'financial_services/transaction_detail.html', {
            'transaction': transaction,
            'related_transaction': related_transaction
        })


@login_required
def get_wallet_balance_api(request, wallet_id):
    wallet = get_object_or_404(CryptoWallet, id=wallet_id, user=request.user)
    return JsonResponse({
        'balance': str(wallet.balance),
        'currency': wallet.wallet_type,
        'address': wallet.address
    })