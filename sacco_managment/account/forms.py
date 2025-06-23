from django import forms
from account.models import KYC
from django.forms import ImageField, FileInput, DateInput, TextInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StaffPermission

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


class StaffCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('SUPPORT', 'Support Staff'),
        ('LOAN_OFFICER', 'Loan Officer'),
        ('ACCOUNT_MANAGER', 'Account Manager'),
        ('ADMIN', 'System Admin'),
    )
    
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    can_view_balances = forms.BooleanField(required=False)
    can_reset_passwords = forms.BooleanField(required=False)
    can_approve_loans = forms.BooleanField(required=False)
    can_edit_kyc = forms.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STAFF'  # Set as staff by default
        if commit:
            user.save()
        return user

class StaffEditForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('SUPPORT', 'Support Staff'),
        ('LOAN_OFFICER', 'Loan Officer'),
        ('ACCOUNT_MANAGER', 'Account Manager'),
        ('ADMIN', 'System Admin'),
    )
    
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    can_view_balances = forms.BooleanField(required=False)
    can_reset_passwords = forms.BooleanField(required=False)
    can_approve_loans = forms.BooleanField(required=False)
    can_edit_kyc = forms.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')