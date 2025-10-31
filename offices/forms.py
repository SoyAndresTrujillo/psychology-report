from django import forms
from django.core.exceptions import ValidationError
from .models import DoctorsOffice
from accounts.models import Account


class DoctorsOfficeForm(forms.ModelForm):
    """
    Form for creating doctor's offices.
    """
    class Meta:
        model = DoctorsOffice
        fields = ['name', 'address', 'phone', 'email', 'psychologist']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Office Name"}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Full Address', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'office@example.com'}),
            'psychologist': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show psychologists in the dropdown
        self.fields['psychologist'].queryset = Account.objects.filter(role='psychologist')
        self.fields['psychologist'].required = False
        self.fields['psychologist'].label = "Managing Psychologist (Optional)"
    
    def clean_phone(self):
        """Basic phone validation"""
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 7:
            raise ValidationError("Please enter a valid phone number.")
        return phone
