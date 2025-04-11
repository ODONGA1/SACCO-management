from django.contrib import admin
from django.utils.html import format_html
from .models import CryptoWallet, CryptoTransaction, ExchangeRate

@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_type', 'formatted_balance', 'is_active', 'created_at')
    list_filter = ('wallet_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'address')
    readonly_fields = ('created_at', 'updated_at', 'qr_code_preview')
    fieldsets = (
        (None, {'fields': ('user', 'wallet_type', 'address')}),
        ('Balance', {'fields': ('balance',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    def formatted_balance(self, obj):
        return f"{obj.balance:.8f} {obj.wallet_type}"
    formatted_balance.short_description = 'Balance'

    def qr_code_preview(self, obj):
        return format_html(f'<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={obj.address}" />')
    qr_code_preview.short_description = 'QR Code'

@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('short_txid', 'user', 'wallet', 'transaction_type', 'formatted_amount', 'status', 'timestamp')
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = ('txid', 'tx_hash', 'user__username')
    readonly_fields = ('txid', 'timestamp', 'metadata_preview')
    date_hierarchy = 'timestamp'
    
    def short_txid(self, obj):
        return f"{obj.txid[:6]}...{obj.txid[-4:]}"
    short_txid.short_description = 'Transaction ID'
    
    def formatted_amount(self, obj):
        return f"{obj.amount:.8f} {obj.wallet.wallet_type}"
    formatted_amount.short_description = 'Amount'
    
    def metadata_preview(self, obj):
        return format_html('<pre>{}</pre>', str(obj.metadata))
    metadata_preview.short_description = 'Metadata'

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('pair', 'rate_type', 'rate', 'provider', 'effective_date', 'is_active')
    list_filter = ('rate_type', 'provider', 'effective_date')
    search_fields = ('base_currency', 'target_currency')
    readonly_fields = ('expires_at',)
    
    def pair(self, obj):
        return f"{obj.base_currency}/{obj.target_currency}"
    pair.short_description = 'Currency Pair'
    
    def is_active(self, obj):
        return obj.expires_at > timezone.now()
    is_active.boolean = True
    is_active.short_description = 'Active'