from django.contrib import admin
from .models import CryptoWallet, CryptoTransaction

@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_type', 'balance', 'created_at')
    list_filter = ('wallet_type',)
    search_fields = ('user__username',)

@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'status', 'timestamp')
    list_filter = ('transaction_type', 'status')
    search_fields = ('wallet__user__username',)
    date_hierarchy = 'timestamp'
