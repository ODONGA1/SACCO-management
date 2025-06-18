from django.contrib import admin
from account.models import Account, KYC
from user_auths.models import User
from import_export.admin import ImportExportModelAdmin

class AccountAdminModel(ImportExportModelAdmin):
    list_editable = ['account_status', 'account_balance', 'kyc_submitted', 'kyc_confirmed'] 
    list_display = ['user', 'account_number' ,'account_status', 'account_balance', 'kyc_submitted', 'kyc_confirmed'] 
    list_filter = ['account_status']

class KYCAdmin(ImportExportModelAdmin):
    search_fields = ["full_name"]
    list_display = ['user', 'full_name', 'gender', 'identity_type', 'date_of_birth'] 


class MobileMoneyTransactionInline(admin.TabularInline):
    model = MobileMoneyTransaction
    extra = 0
    readonly_fields = ('provider', 'phone_number', 'transaction_ref', 'is_reconciled')


class MobileMoneyTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_ref', 'provider', 'phone_number', 'amount', 'is_reconciled']
    list_filter = ['provider', 'is_reconciled']
    search_fields = ['phone_number', 'transaction_ref']
    actions = ['reconcile_transactions']

    def amount(self, obj):
        return obj.transaction.amount
    
    def reconcile_transactions(self, request, queryset):
        for transaction in queryset:
            transaction.is_reconciled = True
            transaction.save()
        self.message_user(request, f"{queryset.count()} transactions reconciled")

admin.site.register(MobileMoneyTransaction, MobileMoneyTransactionAdmin)
admin.site.register(Account, AccountAdminModel)
admin.site.register(KYC, KYCAdmin)
