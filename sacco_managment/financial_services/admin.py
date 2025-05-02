from django.contrib import admin
from .models import CryptoWallet, CryptoTransaction
from django.utils.html import format_html

@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_type', 'balance_display', 'created_at')
    list_filter = ('wallet_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)
    
    
    def balance_display(self, obj):
        return obj.get_balance_display()
    balance_display.short_description = 'Balance'
    
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }

@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'wallet_info', 'transaction_type', 
        'amount_display', 'status', 'timestamp'
    )
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = (
        'wallet__user__username', 
        'wallet__user__email',
        'description'
    )
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    list_select_related = ('wallet', 'wallet__user')
    
    def wallet_info(self, obj):
        return format_html(
            "{}<br><small>{}</small>",
            obj.wallet.user.username,
            obj.wallet.get_wallet_type_display()
        )
    wallet_info.short_description = 'Wallet'
    
    def amount_display(self, obj):
        return f"{obj.amount:.8f} {obj.wallet.wallet_type}"
    amount_display.short_description = 'Amount'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'wallet', 'wallet__user'
        )
        
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }