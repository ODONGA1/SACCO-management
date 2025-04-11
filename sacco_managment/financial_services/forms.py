from django import forms
from django.core.exceptions import ValidationError
from .models import CryptoTransaction, CryptoWallet
from django.utils import timezone
from decimal import Decimal

class CryptoTransactionForm(forms.ModelForm):
    class Meta:
        model = CryptoTransaction
        fields = ['wallet', 'transaction_type', 'amount', 'network_fee']
        widgets = {
            'wallet': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'transaction-type'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0.00000001'
            }),
            'network_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0'
            }),
        }
        labels = {
            'network_fee': 'Network Fee (Optional)'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['wallet'].queryset = CryptoWallet.objects.filter(
                user=self.user, 
                is_active=True
            ).select_related('user')
            
        # Add currency symbols to wallet choices
        wallet_choices = []
        for wallet in self.fields['wallet'].queryset:
            wallet_choices.append((
                wallet.id, 
                f"{wallet.get_wallet_type_display()} ({wallet.wallet_type}) - Balance: {wallet.balance:.8f}"
            ))
        self.fields['wallet'].choices = wallet_choices

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= Decimal('0'):
            raise ValidationError("Amount must be greater than zero")
        return amount

    def clean_network_fee(self):
        fee = self.cleaned_data.get('network_fee', Decimal('0'))
        if fee < Decimal('0'):
            raise ValidationError("Network fee cannot be negative")
        return fee

    def clean(self):
        cleaned_data = super().clean()
        wallet = cleaned_data.get('wallet')
        transaction_type = cleaned_data.get('transaction_type')
        amount = cleaned_data.get('amount')
        fee = cleaned_data.get('network_fee', Decimal('0'))
        
        if wallet and transaction_type and amount:
            if transaction_type in ['SELL', 'SWAP', 'TRANSFER_OUT']:
                total_debit = amount + fee
                if total_debit > wallet.balance:
                    raise ValidationError(
                        f"Insufficient balance. Available: {wallet.balance:.8f} {wallet.wallet_type}, "
                        f"Required: {total_debit:.8f} {wallet.wallet_type}"
                    )
        
        return cleaned_data