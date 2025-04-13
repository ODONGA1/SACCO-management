from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal
import shortuuid
from shortuuid.django_fields import ShortUUIDField

User = get_user_model()

class CryptoWallet(models.Model):
    WALLET_TYPES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('LTC', 'Litecoin'),
        ('XRP', 'Ripple'),
        ('BCH', 'Bitcoin Cash'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    wallet_type = models.CharField(max_length=10, choices=WALLET_TYPES)
    address = models.CharField(
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                regex='^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$',
                message='Invalid Bitcoin address format',
                code='invalid_address'
            ) if wallet_type == 'BTC' else 
            RegexValidator(
                regex='^0x[a-fA-F0-9]{40}$',
                message='Invalid Ethereum address format',
                code='invalid_address'
            ) for wallet_type in [x[0] for x in WALLET_TYPES]
        ][0]
    )
    balance = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('user', 'wallet_type')
        ordering = ['-created_at']
        verbose_name = 'Crypto Wallet'
        verbose_name_plural = 'Crypto Wallets'

    def __str__(self):
        return f"{self.user.username}'s {self.get_wallet_type_display()} Wallet"

    def clean(self):
        if self.balance < Decimal('0'):
            raise ValidationError("Wallet balance cannot be negative")


class CryptoTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('BUY', 'Purchase'),
        ('SELL', 'Sale'),
        ('SWAP_IN', 'Swap In'),
        ('SWAP_OUT', 'Swap Out'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    txid = ShortUUIDField(
        length=16,
        prefix="tx_",
        alphabet='1234567890ABCDEFGHJKLMNPQRSTUVWXYZ',
        unique=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    wallet = models.ForeignKey(
        CryptoWallet,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=12, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    network_fee = models.DecimalField(
        max_digits=12, 
        decimal_places=8, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['txid']),
            models.Index(fields=['user', 'wallet']),
            models.Index(fields=['status', 'timestamp']),
        ]
        verbose_name = 'Crypto Transaction'
        verbose_name_plural = 'Crypto Transactions'

    def __str__(self):
        return f"{self.txid} - {self.get_transaction_type_display()}"

    def save(self, *args, **kwargs):
        if self.status == 'CONFIRMED' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        super().save(*args, **kwargs)


class ExchangeRate(models.Model):
    RATE_TYPES = (
        ('BUY', 'Buy Rate'),
        ('SELL', 'Sell Rate'),
        ('MID', 'Mid Market Rate'),
    )
    
    PROVIDERS = (
        ('BINANCE', 'Binance'),
        ('COINBASE', 'Coinbase'),
        ('KRAKEN', 'Kraken'),
        ('MANUAL', 'Manual Entry'),
    )
    
    base_currency = models.CharField(max_length=3, default='USD')
    target_currency = models.CharField(max_length=4)
    rate_type = models.CharField(max_length=4, choices=RATE_TYPES)
    rate = models.DecimalField(
        max_digits=12, 
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.000001'))]
    )
    provider = models.CharField(max_length=10, choices=PROVIDERS)
    effective_date = models.DateField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=1))
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-effective_date']
        unique_together = ('base_currency', 'target_currency', 'rate_type', 'effective_date')
        verbose_name = 'Exchange Rate'
        verbose_name_plural = 'Exchange Rates'

    def __str__(self):
        return f"{self.base_currency}/{self.target_currency} {self.rate_type} @ {self.rate}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=1)
        super().save(*args, **kwargs)


class CryptoSwap(models.Model):
    txid = ShortUUIDField(
        length=16,
        prefix="swap_",
        alphabet='1234567890ABCDEFGHJKLMNPQRSTUVWXYZ',
        unique=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swaps')
    source_transaction = models.ForeignKey(
        CryptoTransaction, 
        on_delete=models.PROTECT,
        related_name='source_swaps'
    )
    target_transaction = models.ForeignKey(
        CryptoTransaction,
        on_delete=models.PROTECT,
        related_name='target_swaps'
    )
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6)
    swap_fee = models.DecimalField(max_digits=12, decimal_places=8)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Crypto Swap'
        verbose_name_plural = 'Crypto Swaps'

    def __str__(self):
        return f"Swap {self.txid}"