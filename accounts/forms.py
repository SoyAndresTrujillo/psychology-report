from django import forms
from django.core.exceptions import ValidationError
from .models import Account, Role
from offices.models import DoctorsOffice
from doctors.models import Doctor


class AccountForm(forms.ModelForm):
    """Form for creating accounts (patients and psychologists).
    
    Technical Details:
    - Extends Django's ModelForm for Account model
    - Includes conditional fields (doctors_office, specialty) for psychologists
    - Implements three-tier validation: field-level, clean_email/age, and form-level clean
    - Uses Bootstrap form-control class for consistent styling
    
    Conditional Fields:
    - doctors_office: ModelChoiceField for DoctorsOffice (required if role='psychologist')
    - specialty: ChoiceField from Doctor.SPECIALTY_CHOICES (required if role='psychologist')
    
    Validation Pipeline:
    1. clean_email(): Ensures email uniqueness across Account table
    2. clean_age(): Validates age range (1-120)
    3. clean(): Validates psychologist conditional requirements
    
    Form Behavior:
    - All fields use Bootstrap 'form-control' class
    - Role field has 'id_role' for JavaScript conditional field toggling
    - Psychologist fields show help text indicating requirement
    - Empty specialty choice ('-- Select Specialty --') for initial state
    
    Related Models:
    - Account (base model)
    - DoctorsOffice (ForeignKey for psychologists)
    - Doctor (specialty choices reference)
    
    Form Fields:
    - name: CharField for first name (max 100 chars)
    - last_name: CharField for last name (max 100 chars)
    - age: PositiveIntegerField (1-120)
    - gender: ChoiceField (M/F/O from Account.GENDER_CHOICES)
    - phone: CharField for phone number (max 20 chars)
    - email: EmailField with uniqueness validation
    - role: ChoiceField (patient/psychologist from Account.ROLE_CHOICES)
    - doctors_office: ModelChoiceField (conditional, psychologist only)
    - specialty: ChoiceField (conditional, psychologist only)
    
    Validation Rules:
    - Email must be unique across all accounts
    - Age must be between 1 and 120
    - If role is 'psychologist':
        * doctors_office field is required
        * specialty field is required
    - If role is 'patient':
        * doctors_office and specialty are ignored
    
    Database Interactions:
    - Queries DoctorsOffice.objects.all() for office dropdown
    - Checks Account.objects.filter(email=email).exists() for uniqueness
    - Form save() creates Account instance only (Doctor profile created separately)
    
    Usage Example:
        # In views.py
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            if account.role == 'psychologist':
                Doctor.objects.create(
                    account=account,
                    doctors_office=form.cleaned_data['doctors_office'],
                    specialty=form.cleaned_data['specialty']
                )
    
    Related Views:
    - accounts.views.create_account_view: Creates account and optional doctor profile
    - accounts.views.update_account_view: Updates existing account
    
    Related Forms:
    - doctors.forms.DoctorForm: Separate form for doctor profile management
    - offices.forms.DoctorsOfficeForm: Form for creating doctor's offices
    """
    doctors_office = forms.ModelChoiceField(
        queryset=DoctorsOffice.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Doctor's Office",
        help_text="Required for psychologists"
    )
    
    specialty = forms.ChoiceField(
        choices=[('', '-- Select Specialty --')] + Doctor.SPECIALTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Specialty",
        help_text="Required for psychologists"
    )
    
    class Meta:
        """Meta configuration for AccountForm.
        
        Specifies:
        - model: Account model to bind form to
        - fields: List of Account model fields to include
        - widgets: Custom widget configuration for each field
        
        Widget Attributes:
        - class='form-control': Bootstrap styling for all inputs
        - placeholder: User-friendly hints for text inputs
        - min/max: HTML5 validation for age field
        - type='date/time': HTML5 input types where applicable
        - id='id_role': Specific ID for JavaScript conditional logic
        """
        model = Account
        fields = ['name', 'last_name', 'age', 'gender', 'phone', 'email', 'role']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age', 'min': '1', 'max': '120'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'role': forms.Select(attrs={'class': 'form-control', 'id': 'id_role'}),
        }
    
    def clean_email(self):
        """Validate email uniqueness across Account table.
        
        Ensures no duplicate email addresses exist in the database.
        This is a field-level validation method called automatically
        during form validation pipeline.
        
        Technical Details:
        - Called after basic field validation (email format check)
        - Queries Account table for existing email
        - Uses .exists() for efficient database query (no data retrieval)
        - Raises ValidationError if email already exists
        
        Returns:
            str: The validated email address
            
        Raises:
            ValidationError: If email already exists in Account table
            
        Database Query:
            SELECT COUNT(*) FROM accounts_account WHERE email = %s
        """
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    
    def clean_age(self):
        """Validate age is within reasonable range (1-120).
        
        Provides server-side validation for age field in addition to
        HTML5 min/max attributes. Ensures data integrity even if
        client-side validation is bypassed.
        
        Technical Details:
        - Called after basic field validation (positive integer check)
        - Validates age is between 1 and 120 inclusive
        - Complements HTML5 min/max attributes in widget
        
        Validation Logic:
        - age < 1: Invalid (must be at least 1)
        - 1 <= age <= 120: Valid
        - age > 120: Invalid (unrealistic age)
        
        Returns:
            int: The validated age value
            
        Raises:
            ValidationError: If age is outside range [1, 120]
        """
        age = self.cleaned_data.get('age')
        if age and (age < 1 or age > 120):
            raise ValidationError("Please enter a valid age between 1 and 120.")
        return age
    
    def clean(self):
        """Validate conditional fields for psychologists.
        
        Form-level validation that enforces business rules for psychologist accounts.
        This method is called after all field-level clean methods have run.
        
        Business Rules:
        - If role == 'psychologist':
            * doctors_office field must be provided
            * specialty field must be provided
        - If role == 'patient':
            * doctors_office and specialty are optional and ignored
        
        Technical Details:
        - Called after all field-level clean_* methods
        - Uses add_error() to attach errors to specific fields
        - Returns cleaned_data dictionary for form processing
        - Errors prevent form.is_valid() from returning True
        
        Validation Flow:
        1. Get role from cleaned_data
        2. Get doctors_office and specialty from cleaned_data
        3. If role is 'psychologist', check both conditional fields
        4. Add field-specific errors if validation fails
        5. Return cleaned_data for further processing
        
        Args:
            None (uses self.cleaned_data)
            
        Returns:
            dict: The cleaned_data dictionary with validated values
            
        Side Effects:
            - Adds errors to 'doctors_office' field if missing for psychologist
            - Adds errors to 'specialty' field if missing for psychologist
        """
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        doctors_office = cleaned_data.get('doctors_office')
        specialty = cleaned_data.get('specialty')
        
        # If psychologist, require office and specialty
        if role and role.code == 'psychologist':
            if not doctors_office:
                self.add_error('doctors_office', "Doctor's office is required for psychologists.")
            if not specialty:
                self.add_error('specialty', "Specialty is required for psychologists.")
        
        return cleaned_data


class RoleForm(forms.ModelForm):
    """Simple form for creating new roles.
    
    Only requires a name input - the code is auto-generated.
    Follows Single Responsibility Principle.
    """
    
    class Meta:
        model = Role
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter role name (e.g., Manager, Admin)',
                'autofocus': True
            }),
        }
    
    def clean_name(self):
        """Validate role name uniqueness."""
        name = self.cleaned_data.get('name')
        if name:
            # Check if a role with this name already exists
            if Role.objects.filter(name__iexact=name).exists():
                raise ValidationError("A role with this name already exists.")
        return name
