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
                reciever=request.user,
                sender_account=account,
                reciever_account=account,
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