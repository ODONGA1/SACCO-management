from django.contrib import admin
from core.models import Transaction, CreditCard, Notification
from account.models import Account
from django.utils import timezone
from .models import LoanApplication, LoanRepayment

class TransactionAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'status', 'transaction_type']
    list_display = ['user', 'amount', 'status', 'transaction_type', 'reciever', 'sender']
    list_filter = ['transaction_type', 'status']
    search_fields = ['user__username', 'reciever__username', 'sender__username', 'transaction_id']

    def save_model(self, request, obj, form, change):
        """Handle deposit and withdrawal logic in the admin panel."""
        if not change:  # Only handle new transactions
            account = Account.objects.get(user=obj.user)

            if obj.transaction_type == "deposit":
                account.account_balance += obj.amount
                account.save()
            elif obj.transaction_type == "withdrawal":
                if account.account_balance >= obj.amount:
                    account.account_balance -= obj.amount
                    account.save()
                else:
                    raise ValueError("Insufficient balance for withdrawal.")

        super().save_model(request, obj, form, change)

class CreditCardAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'card_type']
    list_display = ['user', 'amount', 'card_type']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'amount', 'date']
    
    
class LoanRepaymentInline(admin.TabularInline):
    model = LoanRepayment
    extra = 0
    readonly_fields = ('payment_date', 'transaction')
    can_delete = False

class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'loan_type', 'amount', 'duration_months', 'status', 'date_applied')
    list_filter = ('status', 'loan_type', 'date_applied')
    search_fields = ('user__username', 'account__account_number')
    readonly_fields = ('date_applied', 'date_approved', 'date_disbursed')
    inlines = [LoanRepaymentInline]
    actions = ['approve_loans', 'reject_loans', 'disburse_loans']

    def approve_loans(self, request, queryset):
        for loan in queryset.filter(status='pending'):
            loan.status = 'approved'
            loan.date_approved = timezone.now()
            loan.save()
            
            Notification.objects.create(
                user=loan.user,
                notification_type="Loan Approved",
                amount=loan.amount,
                message=f"Your {loan.loan_type} loan has been approved"
            )
        self.message_user(request, f"{queryset.count()} loans approved")

    def reject_loans(self, request, queryset):
        for loan in queryset.filter(status='pending'):
            loan.status = 'rejected'
            loan.save()
            
            Notification.objects.create(
                user=loan.user,
                notification_type="Loan Rejected",
                amount=loan.amount,
                message=f"Your {loan.loan_type} loan has been rejected"
            )
        self.message_user(request, f"{queryset.count()} loans rejected")

    def disburse_loans(self, request, queryset):
        for loan in queryset.filter(status='approved'):
            loan.status = 'disbursed'
            loan.date_disbursed = timezone.now()
            loan.save()
            
            # Credit the user's account
            account = loan.account
            account.account_balance += loan.amount
            account.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=loan.user,
                amount=loan.amount,
                transaction_type="loan_disbursement",
                status="completed",
                sender=None,  # System generated
                reciever=loan.user,
                sender_account=None,
                reciever_account=account,
                description=f"Loan disbursement for {loan.loan_type}"
            )
            
            Notification.objects.create(
                user=loan.user,
                notification_type="Loan Disbursed",
                amount=loan.amount,
                message=f"Your {loan.loan_type} loan has been disbursed"
            )
        self.message_user(request, f"{queryset.count()} loans disbursed")


admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(Notification, NotificationAdmin)
