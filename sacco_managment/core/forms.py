from django import forms
from core.models import CreditCard, LoanApplication, Transaction, Notification

class CreditCardForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Card Holder Name"}))
    number = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Card Number"}))
    month = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Expiry Month"}))
    year = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Expiry Month"}))
    cvv = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"CVV"}))

    class Meta:
        model = CreditCard
        fields = ['name', 'number', 'month', 'year', 'cvv', 'card_type']

class AmountForm(forms.ModelForm):
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"UGX30"}))
    
    class Meta:
        model = CreditCard
        fields = ['amount']


class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['loan_type', 'amount', 'duration_months', 'purpose']
        
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Loan amount must be greater than zero")
        return amount
    
    def clean_duration_months(self):
        duration = self.cleaned_data.get('duration_months')
        if duration < 1 or duration > 60:  # Max 5 years
            raise forms.ValidationError("Loan duration must be between 1 and 60 months")
        return duration