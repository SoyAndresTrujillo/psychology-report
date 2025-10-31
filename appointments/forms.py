from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Appointment
from accounts.models import Account


class AppointmentForm(forms.ModelForm):
    """
    Form for creating appointments between patients and psychologists.
    """
    class Meta:
        model = Appointment
        fields = ['patient', 'psychologist', 'date', 'time', 'status']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'psychologist': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter patients and psychologists
        self.fields['patient'].queryset = Account.objects.filter(role='patient')
        self.fields['psychologist'].queryset = Account.objects.filter(role='psychologist')
        self.fields['status'].initial = 'scheduled'
    
    def clean_date(self):
        """Validate that appointment date is not in the past"""
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")
        return date
    
    def clean(self):
        """Validate business rules"""
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        psychologist = cleaned_data.get('psychologist')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        # Validate patient and psychologist are different
        if patient and psychologist and patient == psychologist:
            raise ValidationError("Patient and psychologist cannot be the same person.")
        
        # Validate time slot availability
        if psychologist and date and time:
            conflicting_appointment = Appointment.objects.filter(
                psychologist=psychologist,
                date=date,
                time=time
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            
            if conflicting_appointment:
                raise ValidationError(
                    f"This psychologist already has an appointment at {time} on {date}."
                )
        
        return cleaned_data
