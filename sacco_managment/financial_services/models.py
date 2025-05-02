from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class CryptoWallet(models.Model):
    WALLET_TYPES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    wallet_type = models.CharField(max_length=10, choices=WALLET_TYPES)
    balance = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'wallet_type')
        verbose_name = "Crypto Wallet"
        verbose_name_plural = "Crypto Wallets"

    def __str__(self):
        return f"{self.user.username}'s {self.get_wallet_type_display()} Wallet"

    def get_balance_display(self):
        return f"{self.balance:.8f} {self.wallet_type}"


class CryptoTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    wallet = models.ForeignKey(
        CryptoWallet, 
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    related_transaction = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='related_transactions'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Crypto Transaction"
        verbose_name_plural = "Crypto Transactions"

    def __str__(self):
        return (f"{self.get_transaction_type_display()} of {self.amount:.8f} "
                f"{self.wallet.wallet_type} ({self.get_status_display()})")

    def save(self, *args, **kwargs):
        if not self.timestamp:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('financial_services:transaction_detail', args=[str(self.id)])