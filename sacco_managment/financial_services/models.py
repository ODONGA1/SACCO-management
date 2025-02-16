from django.db import models
from user_auths.models import User
from account.models import Account
from shortuuid.django_fields import ShortUUIDField
from core.models import Transaction

class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=3, default='USD')
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.base_currency}/{self.target_currency}"

class Recipient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nickname} - {self.account_number}"

class CryptoWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bitcoin_balance = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    ethereum_balance = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    usdt_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

class CryptoTransaction(models.Model):
    CRYPTO_TYPES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
    )
    
    transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="CRY")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto_type = models.CharField(max_length=4, choices=CRYPTO_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=8)
    transaction_type = models.CharField(max_length=10, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    fiat_amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class Deposit(models.Model):
    deposit_id = ShortUUIDField(unique=True, length=10, prefix="DEP")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=[('BANK', 'Bank Transfer'), ('CARD', 'Credit Card')])
    status = models.CharField(max_length=20, default='PENDING', choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)

class Withdrawal(models.Model):
    withdrawal_id = ShortUUIDField(unique=True, length=10, prefix="WTH")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=[('BANK', 'Bank Transfer'), ('CRYPTO', 'Crypto Wallet')])
    status = models.CharField(max_length=20, default='PENDING', choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)