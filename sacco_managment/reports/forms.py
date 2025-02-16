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

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Ensure start date is before end date
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be before the end date.")

        # Prevent future dates
        today = timezone.now().date()
        if start_date and start_date > today:
            raise forms.ValidationError("Start date cannot be in the future.")
        if end_date and end_date > today:
            raise forms.ValidationError("End date cannot be in the future.")

        return cleaned_data
