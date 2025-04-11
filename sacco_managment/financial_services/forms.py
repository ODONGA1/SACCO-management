# financial_services/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Recipient, CryptoTransaction, Deposit, Withdrawal
from account.models import Account
from user_auths.models import User

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['nickname', 'account_number', 'bank_name']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        if Recipient.objects.filter(user=self.user, account_number=account_number).exists():
            raise ValidationError("This account number is already registered")
        return account_number

class CryptoPurchaseForm(forms.ModelForm):
    class Meta:
        model = CryptoTransaction
        fields = ['crypto_type', 'amount']
        widgets = {
            'crypto_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        return amount

class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ['amount', 'method']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 10:  # Minimum deposit amount
            raise ValidationError("Minimum deposit amount is UGX10")
        return amount

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'method']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['method'].widget.attrs.update({'class': 'form-select'})

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        try:
            account = Account.objects.get(user=self.user)
            if amount > account.account_balance:
                raise ValidationError("Insufficient funds")
        except Account.DoesNotExist:
            raise ValidationError("Account not found")
        
        if amount < 5:  # Minimum withdrawal amount
            raise ValidationError("Minimum withdrawal amount is $5")
        
        return amount

class ExchangeRateUpdateForm(forms.Form):
    api_key = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="API key for exchange rate service"
    )
    base_currency = forms.ChoiceField(
        choices=[('USD', 'US Dollar'), ('EUR', 'Euro')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )