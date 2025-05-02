from django import forms
from .models import CryptoTransaction, CryptoWallet
from django.core.exceptions import ValidationError

class TransactionForm(forms.ModelForm):
    class Meta:
        model = CryptoTransaction
        fields = ['wallet', 'transaction_type', 'amount', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['wallet'].queryset = CryptoWallet.objects.filter(user=self.user)
            # Set initial wallet if user has only one
            if self.fields['wallet'].queryset.count() == 1:
                self.fields['wallet'].initial = self.fields['wallet'].queryset.first()

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        wallet = cleaned_data.get('wallet')
        amount = cleaned_data.get('amount')
        transaction_type = cleaned_data.get('transaction_type')

        if wallet and amount and transaction_type:
            if transaction_type in ['WITHDRAWAL', 'TRANSFER']:
                if wallet.balance < amount:
                    raise ValidationError(
                        f"Insufficient balance. Available: {wallet.balance} {wallet.wallet_type}"
                    )
        return cleaned_data