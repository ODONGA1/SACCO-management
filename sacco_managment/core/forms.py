from django import forms
from django import forms
from core.models import CreditCard, LoanApplication, PROVIDER_CHOICES


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
        if duration < 1 or duration > 12:  # Max 1 years
            raise forms.ValidationError("Loan duration must be between 1 and 60 months")
        return duration
    
    
class MobileMoneyDepositForm(forms.Form):
    amount = forms.DecimalField(
        label='Amount to Deposit',
        min_value=10,  # Minimum deposit amount
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label='Mobile Money Number',
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    network = forms.ChoiceField(
        label='Mobile Network',
        choices=[
            ('MTN', 'MTN'),
            ('Airtel', 'Airtel'),
            ('Zamtel', 'Zamtel'),
            ('Other', 'Other')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if not phone.startswith('256'):
            raise forms.ValidationError("Phone number must start with 256")
        if len(phone) != 12:
            raise forms.ValidationError("Invalid phone number length")
        return phone


    
    
class MobileMoneyWithdrawalForm(forms.Form):
    phone_number = forms.CharField(max_length=15)
    provider = forms.ChoiceField(choices=PROVIDER_CHOICES)
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=1000)