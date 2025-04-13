from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

# Get the custom User model
User = get_user_model()

# financial_services/models.py
class CryptoWallet(models.Model):
    WALLET_TYPES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet_type = models.CharField(max_length=10, choices=WALLET_TYPES)
    balance = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'wallet_type')

    def __str__(self):
        return f"{self.user.username}'s {self.wallet_type} Wallet"



class CryptoTransaction(models.Model):
    # Transaction types (Deposit, Withdrawal, Transfer)
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    )
    
    # Transaction statuses (Pending, Completed, Failed)
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    # ForeignKey to the CryptoWallet model
    wallet = models.ForeignKey(CryptoWallet, on_delete=models.PROTECT)
    
    # Transaction type (Deposit, Withdrawal, etc.)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    
    # Transaction amount (Decimal for precision)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    
    # Transaction status (Pending, Completed, Failed)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # Timestamp when the transaction is created
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Description of the transaction
    description = models.TextField(blank=True)

    class Meta:
        # Order transactions by timestamp in descending order
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} {self.wallet.wallet_type}"
