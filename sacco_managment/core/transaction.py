
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Transaction
from account.models import Account
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# def transaction_lists(request):
#     sender_transaction = Transaction.objects.filter(sender=request.user, transaction_type="transfer").order_by("-created_at")
#     reciever_transaction = Transaction.objects.filter(reciever=request.user, transaction_type="transfer").order_by("-created_at")

#     request_sender_transaction = Transaction.objects.filter(sender=request.user, transaction_type="request")
#     request_reciever_transaction = Transaction.objects.filter(reciever=request.user, transaction_type="request")

#     context = {
#         "sender_transaction": sender_transaction,
#         "reciever_transaction": reciever_transaction,
#         "request_sender_transaction": request_sender_transaction,
#         "request_reciever_transaction": request_reciever_transaction,
#     }

#     return render(request, "transaction/transaction-list.html", context)

def transaction_lists(request):
    sender_transaction = Transaction.objects.filter(sender=request.user, transaction_type="transfer").order_by("-date")
    reciever_transaction = Transaction.objects.filter(reciever=request.user, transaction_type="transfer").order_by("-date")

    request_sender_transaction = Transaction.objects.filter(sender=request.user, transaction_type="request").order_by("-date")
    request_reciever_transaction = Transaction.objects.filter(reciever=request.user, transaction_type="request").order_by("-date")

    context = {
        "sender_transaction": sender_transaction,
        "reciever_transaction": reciever_transaction,
        "request_sender_transaction": request_sender_transaction,
        "request_reciever_transaction": request_reciever_transaction,
    }

    return render(request, "transaction/transaction-list.html", context)



@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    if request.user not in [transaction.sender, transaction.reciever]:
        messages.error(request, "You are not authorized to view this transaction.")
        return redirect("transaction:transaction_lists")

    context = {"transaction": transaction}
    return render(request, "transaction/transaction-detail.html", context)

@login_required
def deposit_money(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        pin_number = request.POST.get("pin-number")

        if pin_number == request.user.account.pin_number:
            request.user.account.account_balance += float(amount)
            request.user.account.save()

            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type="deposit",
                status="completed",
                sender=request.user,
                reciever=request.user,
                sender_account=request.user.account,
                reciever_account=request.user.account
            )
            messages.success(request, "Deposit successful!")
            return redirect("transaction:transaction_lists")
        else:
            messages.error(request, "Incorrect PIN.")
    
    return render(request, "transaction/deposit.html")

@login_required
def withdraw_money(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        pin_number = request.POST.get("pin-number")
        
        if pin_number == request.user.account.pin_number:
            if request.user.account.account_balance >= float(amount):
                request.user.account.account_balance -= float(amount)
                request.user.account.save()

                Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type="withdrawal",
                    status="completed",
                    sender=request.user,
                    reciever=request.user,
                    sender_account=request.user.account,
                    reciever_account=request.user.account
                )
                messages.success(request, "Withdrawal successful!")
                return redirect("transaction:transaction_lists")
            else:
                messages.error(request, "Insufficient balance.")
        else:
            messages.error(request, "Incorrect PIN.")
    
    return render(request, "transaction/withdraw.html")
