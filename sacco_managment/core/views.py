from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import LoanApplication, LoanRepayment, Notification, Transaction, LOAN_TYPES, LOAN_STATUS
from account.models import Account
from .forms import LoanApplicationForm
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from .models import MobileMoneyTransaction
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
import json
from .forms import MobileMoneyDepositForm, MobileMoneyWithdrawalForm
from django.conf import settings
from django.utils import timezone

def index(request):
    if request.user.is_authenticated:
        return redirect("account:account")
    return render(request, "core/index.html")

def contact(request):
    return render(request, "core/contact.html")

def about(request):
    return render(request, "core/about.html")

@login_required
def apply_for_loan(request):
    account = request.user.account
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.account = account
            
            # Set interest rate based on loan type
            if loan.loan_type == 'personal':
                loan.interest_rate = 12.0  # 12% for personal loans
            elif loan.loan_type == 'business':
                loan.interest_rate = 10.0  # 10% for business loans
            elif loan.loan_type == 'emergency':
                loan.interest_rate = 15.0  # 15% for emergency loans
            else:  # education
                loan.interest_rate = 8.0   # 8% for education loans
                
            loan.save()
            
            # Create notification for admin
            Notification.objects.create(
                user=request.user,
                notification_type="Loan Application",
                amount=loan.amount,
                message=f"New loan application for {loan.amount}"
            )
            
            messages.success(request, "Loan application submitted successfully!")
            return redirect('core:loan-status')
    else:
        form = LoanApplicationForm()
    
    context = {
        'form': form,
        'active_loans': LoanApplication.objects.filter(user=request.user, is_active=True).count(),
        'total_loans': LoanApplication.objects.filter(user=request.user).count(),
    }
    return render(request, 'loan/apply.html', context)

@login_required
def loan_status(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-date_applied')
    context = {
        'loans': loans
    }
    return render(request, 'loan/status.html', context)

@login_required
def loan_detail(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    repayments = loan.repayments.all()
    total_paid = repayments.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = loan.total_repayment - total_paid
    
    context = {
        'loan': loan,
        'repayments': repayments,
        'total_paid': total_paid,
        'balance': balance,
    }
    return render(request, 'loan/detail.html', context)

@login_required
def repay_loan(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    account = request.user.account
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        
        if account.account_balance >= amount:
            # Deduct from account
            account.account_balance -= amount
            account.save()
            
            # Create repayment record
            repayment = LoanRepayment.objects.create(
                loan=loan,
                amount=amount,
                is_paid=True
            )
            
            # Create transaction record
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type="loan_repayment",
                status="completed",
                sender=request.user,
                receiver=request.user,
                sender_account=account,
                receiver_account=account,
                description=f"Loan repayment for {loan.loan_type}"
            )
            
            repayment.transaction = transaction
            repayment.save()
            
            # Check if loan is fully paid
            total_paid = loan.repayments.aggregate(Sum('amount'))['amount__sum'] or 0
            if total_paid >= loan.total_repayment:
                loan.status = 'completed'
                loan.is_active = False
                loan.save()
                
                Notification.objects.create(
                    user=request.user,
                    notification_type="Loan Completion",
                    amount=loan.amount,
                    message=f"Your {loan.loan_type} loan has been fully repaid"
                )
            
            messages.success(request, "Loan repayment successful!")
            return redirect('core:loan-detail', loan_id=loan.id)
        else:
            messages.error(request, "Insufficient funds for repayment")
    
    context = {
        'loan': loan,
        'monthly_repayment': loan.monthly_repayment,
    }
    return render(request, 'loan/repay.html', context)



@login_required
def loan_history(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-date_applied')
    return render(request, 'loan/history.html', {'loans': loans})

#  All repayments (across all loans)
@login_required
def repayment_history(request):
    repayments = LoanRepayment.objects.filter(loan__user=request.user).order_by('-payment_date')
    return render(request, 'loan/repayment_history.html', {'repayments': repayments})



@login_required
def mobile_money_transactions(request):
    deposits = Transaction.objects.filter(
        user=request.user,
        transaction_type='mobile_money_deposit'
    ).order_by('-date')
    
    withdrawals = Transaction.objects.filter(
        user=request.user,
        transaction_type='mobile_money_withdrawal'
    ).order_by('-date')
    
    return render(request, 'mobile_money/transactions.html', {
        'deposits': deposits,
        'withdrawals': withdrawals
    })
    

@login_required
def mobile_money_deposit(request):
    if request.method == 'POST':
        form = MobileMoneyDepositForm(request.POST)
        if form.is_valid():
            # Initiate payment via Flutterwave/Yo! API
            ref = f"MMD-{timezone.now().timestamp()}"
            
            # Create pending transaction
            transaction = Transaction.objects.create(
                user=request.user,
                amount=form.cleaned_data['amount'],
                transaction_type="mobile_money_deposit",
                status="pending",
                description=f"Mobile Money Deposit to {form.cleaned_data['phone_number']}"
            )
            
            MobileMoneyTransaction.objects.create(
                transaction=transaction,
                provider=form.cleaned_data['provider'],
                phone_number=form.cleaned_data['phone_number'],
                transaction_ref=ref
            )
            
            # Simulate API response
            return render(request, 'mobile_money/payment_prompt.html', {
                'phone': form.cleaned_data['phone_number'],
                'amount': form.cleaned_data['amount'],
                'ref': ref
            })
    else:
        form = MobileMoneyDepositForm()
    
    return render(request, 'mobile_money/deposit.html', {
        'form': form,
        'account': request.user.account
    })

@login_required
def mobile_money_withdrawal(request):
    if request.method == 'POST':
        form = MobileMoneyWithdrawalForm(request.POST)
        if form.is_valid():
            account = request.user.account
            amount = form.cleaned_data['amount']
            
            if account.available_balance < amount:
                messages.error(request, "Insufficient funds")
                return redirect('core:mobile-money-withdrawal')
            
            # Create withdrawal request
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type="mobile_money_withdrawal",
                status="pending",
                description=f"Mobile Money Withdrawal to {form.cleaned_data['phone_number']}"
            )
            
            MobileMoneyTransaction.objects.create(
                transaction=transaction,
                provider=form.cleaned_data['provider'],
                phone_number=form.cleaned_data['phone_number'],
                transaction_ref=f"MMW-{timezone.now().timestamp()}"
            )
            
            # Lock funds
            account.locked_funds += amount
            account.save()
            
            messages.success(request, "Withdrawal request submitted. Waiting for admin approval.")
            return redirect('account:account')
    else:
        form = MobileMoneyWithdrawalForm()
    
    return render(request, 'mobile_money/withdrawal.html', {'form': form})

@csrf_exempt
def mobile_money_webhook(request):
    # This would be called by Flutterwave/MTN/Airtel API
    payload = json.loads(request.body)
    ref = payload['tx_ref']
    
    try:
        mm_transaction = MobileMoneyTransaction.objects.get(transaction_ref=ref)
        transaction = mm_transaction.transaction
        
        if payload['status'] == 'successful':
            # Update transaction status
            transaction.status = 'completed'
            transaction.save()
            
            # Update account balance
            account = transaction.user.account
            
            if transaction.transaction_type == 'mobile_money_deposit':
                account.mobile_money_balance += transaction.amount
                Notification.objects.create(
                    user=transaction.user,
                    notification_type="Mobile Money Deposit",
                    amount=transaction.amount,
                    message=f"Mobile Money deposit of UGX {transaction.amount} received"
                )
            elif transaction.transaction_type == 'mobile_money_withdrawal':
                account.locked_funds -= transaction.amount
                Notification.objects.create(
                    user=transaction.user,
                    notification_type="Mobile Money Withdrawal",
                    amount=transaction.amount,
                    message=f"Mobile Money withdrawal of UGX {transaction.amount} processed"
                )
            
            account.save()
            mm_transaction.is_reconciled = True
            mm_transaction.save()
            
            return JsonResponse({'status': 'success'})
    
    except MobileMoneyTransaction.DoesNotExist:
        pass
    
    return JsonResponse({'status': 'failed'}, status=400)
    
    # core/views.py
@staff_member_required
def reconciliation_dashboard(request):
    unreconciled = MobileMoneyTransaction.objects.filter(
        is_reconciled=False
    ).select_related('transaction')
    
    today = timezone.now().date()
    daily_deposits = Transaction.objects.filter(
        transaction_type='mobile_money_deposit',
        status='completed',
        date__date=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'admin/reconciliation.html', {
        'unreconciled': unreconciled,
        'daily_deposits': daily_deposits,
        'deposit_limits': settings.MOBILE_MONEY_CONFIG['DEPOSIT_LIMITS']
    })
    
    
    
@login_required
def mobile_money_transactions(request):
    deposits = Transaction.objects.filter(
        user=request.user,
        transaction_type='mobile_money_deposit'
    ).select_related('mobile_money').order_by('-date')
    
    withdrawals = Transaction.objects.filter(
        user=request.user,
        transaction_type='mobile_money_withdrawal'
    ).select_related('mobile_money').order_by('-date')
    
    return render(request, 'mobile_money/transactions.html', {
        'deposits': deposits,
        'withdrawals': withdrawals
    })