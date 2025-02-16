# reports/forms.py
from django import forms
from django.utils import timezone

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().replace(day=1)
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now()
    )
    format = forms.ChoiceField(
        choices=(('PDF', 'PDF'), ('EXCEL', 'Excel')),
        widget=forms.Select(attrs={'class': 'form-select'})
    )