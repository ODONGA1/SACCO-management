from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import CryptoWallet, CryptoTransaction, ExchangeRate, CryptoSwap

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
        ('Metadata', {'fields': ('created_at', 'updated_at', 'metadata')}),
    )

    def formatted_balance(self, obj):
        return f"{obj.balance:.8f} {obj.wallet_type}"
    formatted_balance.short_description = 'Balance'

    def qr_code_preview(self, obj):
        if obj.address:
            return format_html(
                '<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={}" width="150" height="150" />',
                obj.address
            )
        return "No Address"
    qr_code_preview.short_description = 'QR Code'

@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('short_txid', 'user', 'wallet', 'transaction_type', 'formatted_amount', 'status', 'timestamp')
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = ('txid', 'tx_hash', 'user__username', 'wallet__address')
    readonly_fields = ('txid', 'timestamp', 'confirmed_at', 'ip_address', 'metadata_preview')
    date_hierarchy = 'timestamp'
    actions = ['mark_as_confirmed', 'mark_as_failed']

    def short_txid(self, obj):
        return f"{obj.txid[:6]}...{obj.txid[-4:]}" if obj.txid else "N/A"
    short_txid.short_description = 'Transaction ID'

    def formatted_amount(self, obj):
        return f"{obj.amount:.8f} {obj.wallet.wallet_type}" if obj.wallet else f"{obj.amount:.8f}"
    formatted_amount.short_description = 'Amount'

    def metadata_preview(self, obj):
        return format_html('<pre>{}</pre>', str(obj.metadata))
    metadata_preview.short_description = 'Metadata'

    @admin.action(description='Mark selected transactions as confirmed')
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='CONFIRMED', confirmed_at=timezone.now())
        self.message_user(request, f"{updated} transaction(s) marked as confirmed.")

    @admin.action(description='Mark selected transactions as failed')
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='FAILED')
        self.message_user(request, f"{updated} transaction(s) marked as failed.")

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('pair', 'rate_type', 'rate', 'provider', 'effective_date', 'is_active_display')
    list_filter = ('rate_type', 'provider', 'effective_date')
    search_fields = ('base_currency', 'target_currency')
    readonly_fields = ('expires_at', 'last_updated')
    list_editable = ('rate',)

    def pair(self, obj):
        return f"{obj.base_currency}/{obj.target_currency}"
    pair.short_description = 'Currency Pair'

    def is_active_display(self, obj):
        return obj.expires_at > timezone.now()
    is_active_display.boolean = True
    is_active_display.short_description = 'Active'

@admin.register(CryptoSwap)
class CryptoSwapAdmin(admin.ModelAdmin):
    list_display = ('txid', 'user', 'source_currency', 'target_currency', 'exchange_rate', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('txid', 'user__username')
    readonly_fields = ('timestamp', 'metadata_preview')

    def source_currency(self, obj):
        return obj.source_transaction.wallet.wallet_type if obj.source_transaction and obj.source_transaction.wallet else "N/A"
    source_currency.short_description = 'Source Currency'

    def target_currency(self, obj):
        return obj.target_transaction.wallet.wallet_type if obj.target_transaction and obj.target_transaction.wallet else "N/A"
    target_currency.short_description = 'Target Currency'

    def metadata_preview(self, obj):
        return format_html('<pre>{}</pre>', str(obj.metadata))
    metadata_preview.short_description = 'Metadata'
