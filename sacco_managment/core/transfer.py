from django.shortcuts import render, redirect
from account.models import Account
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from core.models import Transaction, Notification


@login_required
def search_users_account_number(request):
    # account = Account.objects.filter(account_status="active")
    account = Account.objects.all()
    query = request.POST.get("account_number")  # 217703423324

    if query:
        account = account.filter(
            Q(account_number=query) |
            Q(account_id=query)
        ).distinct()

    context = {
        "account": account,
        "query": query,
    }
    return render(request, "transfer/search-user-by-account-number.html", context)


def AmountTransfer(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
    except:
        messages.warning(request, "Account does not exist.")
        return redirect("core:search-account")
    context = {
        "account": account,
    }
    return render(request, "transfer/amount-transfer.html", context)


def AmountTransferProcess(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
    except Account.DoesNotExist:
        messages.warning(request, "Account does not exist.")
        return redirect("core:search-account")

    sender = request.user
    receiver = account.user

    sender_account = request.user.account
    receiver_account = account

    if request.method == "POST":
        amount_str = request.POST.get("amount-send", "").strip()
        description = request.POST.get("description", "").strip()

        # Validate empty input
        if not amount_str:
            messages.error(request, "Please enter an amount.")
            return redirect("core:amount-transfer", account.account_number)

        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            messages.error(request, "Invalid amount. Please enter a valid number.")
            return redirect("core:amount-transfer", account.account_number)

        if amount <= 0:
            messages.error(request, "Amount must be greater than zero.")
            return redirect("core:amount-transfer", account.account_number)

        if sender_account.account_balance >= amount:
            new_transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                description=description,
                receiver=receiver,
                sender=sender,
                sender_account=sender_account,
                receiver_account=receiver_account,
                status="processing",
                transaction_type="transfer"
            )
            return redirect("core:transfer-confirmation", account.account_number, new_transaction.transaction_id)
        else:
            messages.warning(request, "Insufficient funds.")
            return redirect("core:amount-transfer", account.account_number)

    messages.warning(request, "An error occurred. Try again later.")
    return redirect("account:account")


def TransferConfirmation(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transaction does not exist.")
        return redirect("account:account")
    context = {
        "account": account,
        "transaction": transaction
    }
    return render(request, "transfer/transfer-confirmation.html", context)


def TransferProcess(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    sender = request.user
    receiver = account.user

    sender_account = request.user.account
    receiver_account = account

    completed = False

    if request.method == "POST":
        pin_number = request.POST.get("pin-number")
        print(pin_number)

        if pin_number == sender_account.pin_number:
            transaction.status = "completed"
            transaction.save()

            # Remove the amount that i am sending from my account balance and update my account
            sender_account.account_balance -= transaction.amount
            sender_account.save()

            # Add the amount that vas removed from my account to the person that i am sending the money too
            account.account_balance += transaction.amount
            account.save()

            # Create Notification Object
            Notification.objects.create(
                amount=transaction.amount,
                user=account.user,
                notification_type="Credit Alert"
            )

            Notification.objects.create(
                user=sender,
                notification_type="Debit Alert",
                amount=transaction.amount
            )

            messages.success(request, "Transfer Successfull.")
            return redirect("core:transfer-completed", account.account_number, transaction.transaction_id)
        else:
            messages.warning(request, "Incorrect Pin.")
            return redirect('core:transfer-confirmation', account.account_number, transaction.transaction_id)
    else:
        messages.warning(request, "An error occured, Try again later.")
        return redirect('account:account')


def TransferCompleted(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transfer does not exist.")
        return redirect("account:account")
    context = {
        "account": account,
        "transaction": transaction
    }
    return render(request, "transfer/transfer-completed.html", context)
