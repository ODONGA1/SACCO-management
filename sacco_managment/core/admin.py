from django.contrib import admin
from core.models import Transaction, CreditCard, Notification
from account.models import Account

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

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(Notification, NotificationAdmin)
