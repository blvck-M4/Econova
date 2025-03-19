from django import forms
from .models import MonthlyRevenue

class MonthlyRevenueForm(forms.ModelForm):
    class Meta:
        model = MonthlyRevenue
        fields = ['month', 'revenue']  # Ensure 'month' is a DateField

    # Optionally, you can add a DateInput widget to format the date field
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Month',
    )