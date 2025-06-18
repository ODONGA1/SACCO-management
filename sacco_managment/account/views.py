from django.shortcuts import render, redirect
from account.models import KYC, Account
from account.forms import KYCForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.forms import CreditCardForm
from core.models import CreditCard, Notification, Transaction
from django.views.decorators.csrf import csrf_exempt
from .models import MobileMoneyTransaction

@login_required
def account(request):
    if request.user.is_authenticated:
        try:
            kyc = KYC.objects.get(user=request.user)
        except KYC.DoesNotExist:
            messages.warning(request, "You need to submit your KYC")
            return redirect("account:kyc-reg")

        account = Account.objects.get(user=request.user)
    else:
        messages.warning(request, "You need to login to access the dashboard")
        return redirect("user_auths:login")

    context = {
        "kyc": kyc,
        "account": account,
    }
    return render(request, "account/account.html", context)


@login_required
def kyc_registration(request):
    user = request.user
    account = Account.objects.get(user=user)

    try:
        kyc = KYC.objects.get(user=user)
    except KYC.DoesNotExist:
        kyc = None

    if request.method == "POST":
        form = KYCForm(request.POST, request.FILES, instance=kyc)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = user
            new_form.account = account
            new_form.save()
            messages.success(
                request, "KYC Form submitted successfully, In review now.")
            return redirect("account:account")
    else:
        form = KYCForm(instance=kyc)
    context = {
        "account": account,
        "form": form,
        "kyc": kyc,
    }
    return render(request, "account/kyc-form.html", context)


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        try:
            kyc = KYC.objects.get(user=request.user)
        except KYC.DoesNotExist:
            messages.warning(request, "You need to submit your KYC")
            return redirect("account:kyc-reg")

        recent_transfer = Transaction.objects.filter(
            sender=request.user, transaction_type="transfer", status="completed").order_by("-id")[:1]
        recent_received_transfer = Transaction.objects.filter(
            reciever=request.user, transaction_type="transfer").order_by("-id")[:1]

        sender_transaction = Transaction.objects.filter(
            sender=request.user, transaction_type="transfer").order_by("-id")
        receiver_transaction = Transaction.objects.filter(
            reciever=request.user, transaction_type="transfer").order_by("-id")

        request_sender_transaction = Transaction.objects.filter(
            sender=request.user, transaction_type="request")
        request_receiver_transaction = Transaction.objects.filter(
            reciever=request.user, transaction_type="request")

        withdrawal_transactions = Transaction.objects.filter(
            sender=request.user, transaction_type="withdrawal").order_by("-id")

        account = Account.objects.get(user=request.user)
        credit_card = CreditCard.objects.filter(
            user=request.user).order_by("-id")

        # Fetch notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user).order_by('-date')

        if request.method == "POST":
            form = CreditCardForm(request.POST)
            if form.is_valid():
                new_form = form.save(commit=False)
                new_form.user = request.user
                new_form.save()

                Notification.objects.create(
                    user=request.user,
                    notification_type="Added Credit Card"
                )

                messages.success(request, "Card Added Successfully.")
                return redirect("account:dashboard")
        else:
            form = CreditCardForm()

    else:
        messages.warning(request, "You need to login to access the dashboard")
        return redirect("user_auths:login")

    context = {
        "kyc": kyc,
        "account": account,
        "form": form,
        "credit_card": credit_card,
        "sender_transaction": sender_transaction,
        "receiver_transaction": receiver_transaction,
        "request_sender_transaction": request_sender_transaction,
        "request_receiver_transaction": request_receiver_transaction,
        "recent_transfer": recent_transfer,
        "recent_received_transfer": recent_received_transfer,
        "withdrawal_transactions": withdrawal_transactions,
        "notifications": notifications,  # Pass notifications to the template
    }
    return render(request, "account/dashboard.html", context)



@login_required
def all_credit_cards(request):
    cards = CreditCard.objects.filter(user=request.user)
    return render(request, "credit_card/all-card.html", {"credit_cards": cards})


@login_required
def mobile_money_deposit(request):
    if request.method == 'POST':
        form = MobileMoneyDepositForm(request.POST)
        if form.is_valid():
            # Initiate payment via Flutterwave/Yo! API
            # This is a simulation - replace with actual API call
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
    
    return render(request, 'mobile_money/deposit.html', {'form': form})

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