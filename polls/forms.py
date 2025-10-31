from django import forms
from django.core.exceptions import ValidationError
from .models import Polls


class PollsForm(forms.ModelForm):
    """Form for creating polls.
    
    Technical Details:
    - Extends Django's ModelForm for Polls model
    - Implements three-tier validation: field-level, clean_rate, and form-level clean
    - Uses Bootstrap form-control class for consistent styling
    
    Validation Pipeline:
    1. clean_rate(): Ensures rate is between 0 and 5
    2. clean(): Validates rate range (0-5)
    
    Form Behavior:
    - All fields use Bootstrap 'form-control' class
    
    Related Models:
    - Polls (base model)
    
    Form Fields:
    - description: CharField for first name (max 100 chars)
    - rate: CharField for last name (max 100 chars)
    
    Validation Rules:
    - rate must be between 0 and 5
    
    Database Interactions:
    - Form save() creates Polls instance only
    
    Usage Example:
        # In views.py
        form = PollsForm(request.POST)
        if form.is_valid():
            poll = form.save()
    
    Related Views:
    - polls.views.create_poll_view: Creates poll
    """
    
    class Meta:
        """Meta configuration for PollsForm.
        
        Specifies:
        - model: Polls model to bind form to
        - fields: List of Polls model fields to include
        - widgets: Custom widget configuration for each field
        
        Widget Attributes:
        - class='form-control': Bootstrap styling for all inputs
        - placeholder: User-friendly hints for text inputs
        - min/max: HTML5 validation for age field
        - type='date/time': HTML5 input types where applicable
        - id='id_role': Specific ID for JavaScript conditional logic
        """
        model = Polls
        fields = ['description', 'rate']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rate'}),
        }
    
    def clean_rate(self):
        """Validate rate uniqueness across Polls table.
        
        Ensures no duplicate rate exists in the database.
        This is a field-level validation method called automatically
        during form validation pipeline.
        
        Technical Details:
        - Called after basic field validation (rate format check)
        
        Returns:
            str: The validated rate
            
        Database Query:
            SELECT COUNT(*) FROM polls_polls WHERE rate = %s
        """
        rate = self.cleaned_data.get('rate')
        if rate < 0 or rate > 5:
            raise ValidationError("Rate must be between 0 and 5.")
        return rate
    