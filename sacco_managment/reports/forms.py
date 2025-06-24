from django import forms
from django.utils import timezone
from datetime import timedelta

class DateRangeForm(forms.Form):
    REPORT_FORMATS = (
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date() - timedelta(days=30)
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    format = forms.ChoiceField(
        choices=REPORT_FORMATS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='PDF'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Start date cannot be after end date.")
            if (end_date - start_date).days > 365:
                raise forms.ValidationError("Date range cannot exceed 1 year.")
        
        return cleaned_data