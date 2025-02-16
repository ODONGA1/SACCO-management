from django.contrib import admin
from django.utils.html import format_html
from .models import ExchangeRate, Recipient, CryptoWallet, CryptoTransaction, Deposit, Withdrawal

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'current_rate', 'last_updated')
    list_filter = ('base_currency', 'target_currency')
    search_fields = ('target_currency',)
    readonly_fields = ('last_updated',)
    list_per_page = 20
    
    def current_rate(self, obj):
        return f"1 {obj.base_currency} = {obj.rate:.4f} {obj.target_currency}"
    current_rate.short_description = 'Exchange Rate'

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'bank_display', 'account_number', 'created_at')
    search_fields = ('nickname', 'account_number', 'bank_name')
    list_filter = ('bank_name', 'created_at')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    
    def bank_display(self, obj):
        return obj.bank_name[:25] + '...' if len(obj.bank_name) > 25 else obj.bank_name
    bank_display.short_description = 'Bank'

@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'bitcoin_balance', 'ethereum_balance', 'usdt_balance')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
    readonly_fields = ('bitcoin_balance', 'ethereum_balance', 'usdt_balance')
    
    def has_add_permission(self, request):
        return False  # Wallets should be created programmatically

@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'crypto_type', 'amount', 'transaction_type', 
                   'fiat_amount', 'timestamp')
    list_filter = ('transaction_type', 'crypto_type')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 25

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('deposit_id', 'user', 'amount', 'method', 'status', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('deposit_id', 'user__username')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed', 'mark_as_pending']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
    mark_as_completed.short_description = "Mark selected deposits as completed"
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='PENDING')
    mark_as_pending.short_description = "Mark selected deposits as pending"

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('withdrawal_id', 'user', 'amount', 'method', 'status', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('withdrawal_id', 'user__username')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        # Implement CSV export logic
        pass
    export_as_csv.short_description = "Export Selected Withdrawals as CSV"

# Optional: Add admin dashboard customization
admin.site.site_header = "Prime SACCO Financial Administration"
admin.site.site_title = "Financial Services Admin"
admin.site.index_title = "Financial Services Management"