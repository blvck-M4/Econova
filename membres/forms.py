from django import forms
from .models import RevenueMensuelle

class RevenueMensuelleForms(forms.ModelForm):
    class Meta:
        model = RevenueMensuelle
        fields = ['month', 'revenue']  # Ensure 'month' is a DateField

    # Optionally, you can add a DateInput widget to format the date field
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Month',
    )