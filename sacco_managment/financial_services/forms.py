from django import forms
from .models import CryptoTransaction, CryptoWallet

class TransactionForm(forms.ModelForm):
    class Meta:
        model = CryptoTransaction
        fields = ['wallet', 'transaction_type', 'amount', 'description']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['wallet'].queryset = CryptoWallet.objects.filter(user=self.user)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive")
        return amount