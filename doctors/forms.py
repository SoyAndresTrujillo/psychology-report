from django import forms
from django.core.exceptions import ValidationError
from .models import Doctor
from accounts.models import Account
from offices.models import DoctorsOffice


class DoctorForm(forms.ModelForm):
    """
    Form for creating doctor profiles (links psychologists to offices).
    """
    class Meta:
        model = Doctor
        fields = ['account', 'doctors_office', 'specialty']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-control'}),
            'doctors_office': forms.Select(attrs={'class': 'form-control'}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show psychologists who don't already have a doctor profile
        existing_doctor_accounts = Doctor.objects.values_list('account_id', flat=True)
        self.fields['account'].queryset = Account.objects.filter(
            role='psychologist'
        ).exclude(id__in=existing_doctor_accounts)
        self.fields['account'].label = "Psychologist Account"
        self.fields['doctors_office'].label = "Doctor's Office"
    
    def clean_account(self):
        """Validate that account is a psychologist and doesn't have a profile"""
        account = self.cleaned_data.get('account')
        if account:
            if account.role != 'psychologist':
                raise ValidationError("Only psychologist accounts can have doctor profiles.")
            if hasattr(account, 'doctor_profile'):
                raise ValidationError("This psychologist already has a doctor profile.")
        return account
