from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .models import CryptoWallet

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['wallet'].queryset = CryptoWallet.objects.filter(
                user=self.user, 
                is_active=True
            ).select_related('user')
            
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
            if transaction_type in ['SELL', 'SWAP_OUT', 'TRANSFER_OUT']:
                total_debit = amount + fee
                if total_debit > wallet.balance:
                    raise ValidationError(
                        f"Insufficient balance. Available: {wallet.balance:.8f} {wallet.wallet_type}, "
                        f"Required: {total_debit:.8f} {wallet.wallet_type}"
                    )
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if self.request:
            instance.ip_address = self.request.META.get('REMOTE_ADDR')
        if commit:
            instance.save()
        return instance


class CryptoSwapForm(forms.Form):
    source_wallet = forms.ModelChoiceField(
        queryset=CryptoWallet.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    target_currency = forms.ChoiceField(
        choices=CryptoWallet.WALLET_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.00000001',
            'min': '0.00000001'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['source_wallet'].queryset = CryptoWallet.objects.filter(
                user=self.user, 
                is_active=True
            )

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= Decimal('0'):
            raise ValidationError("Amount must be greater than zero")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        source_wallet = cleaned_data.get('source_wallet')
        amount = cleaned_data.get('amount')
        
        if source_wallet and amount:
            if amount > source_wallet.balance:
                raise ValidationError("Insufficient balance in source wallet")
            
            if source_wallet.wallet_type == cleaned_data.get('target_currency'):
                raise ValidationError("Cannot swap to the same currency")
        
        return cleaned_data


class CryptoTransferForm(forms.Form):
    wallet = forms.ModelChoiceField(
        queryset=CryptoWallet.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    recipient_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter recipient wallet address'
        })
    )
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.00000001',
            'min': '0.00000001'
        })
    )
    network_fee = forms.DecimalField(
        max_digits=12,
        decimal_places=8,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.00000001',
            'min': '0'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['wallet'].queryset = CryptoWallet.objects.filter(
                user=self.user, 
                is_active=True
            )

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

    def clean_recipient_address(self):
        address = self.cleaned_data['recipient_address'].strip()
        wallet_type = self.cleaned_data.get('wallet').wallet_type if self.cleaned_data.get('wallet') else None
        
        if wallet_type == 'BTC' and not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')):
            raise ValidationError("Invalid Bitcoin address format")
        elif wallet_type == 'ETH' and not (address.startswith('0x') and len(address) == 42):
            raise ValidationError("Invalid Ethereum address format")
        
        return address

    def clean(self):
        cleaned_data = super().clean()
        wallet = cleaned_data.get('wallet')
        amount = cleaned_data.get('amount')
        fee = cleaned_data.get('network_fee', Decimal('0'))
        
        if wallet and amount:
            if amount + fee > wallet.balance:
                raise ValidationError("Insufficient balance including network fee")
        
        return cleaned_data