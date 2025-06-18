from django import forms
from account.models import KYC
from .models import PROVIDER_CHOICES
from django.forms import ImageField, FileInput, DateInput, TextInput


class DateInput(forms.DateInput):
    input_type = 'date'


class KYCForm(forms.ModelForm):
    identity_image = ImageField(widget=FileInput)
    image = ImageField(widget=FileInput)
    signature = ImageField(widget=FileInput)

    class Meta:
        model = KYC
        fields = ['full_name', 'image', 'marrital_status', 'gender', 'identity_type',
                  'identity_image', 'date_of_birth', 'signature', 'country', 'state', 'city', 'mobile', 'fax']
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "mobile": forms.TextInput(attrs={"placeholder": "Mobile Number"}),
            "fax": forms.TextInput(attrs={"placeholder": "Fax Number"}),
            "country": forms.TextInput(attrs={"placeholder": "Country"}),
            "state": forms.TextInput(attrs={"placeholder": "State"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            'date_of_birth': DateInput
        }


class MobileMoneyDepositForm(forms.Form):
    phone_number = forms.CharField(max_length=15)
    provider = forms.ChoiceField(choices=PROVIDER_CHOICES)
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000)

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
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000)
