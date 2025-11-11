- Start Date: 2025-10-12
- Members: Cascade AI, Andres Trujillo
- RFC PR: N/A

# Summary

Design and implementation of a Django-based psychologist appointment management system that handles patient registration, psychologist profiles, doctor's office management, and appointment scheduling with comprehensive reporting capabilities.

# Problem Summary

The system needs to manage the complete lifecycle of psychological services delivery:
- **Account Management**: Track patients and psychologists with role-based differentiation
- **Office Management**: Maintain doctor's office information with associated psychologists
- **Doctor Profiles**: Link psychologists to offices with specialty information
- **Appointment Scheduling**: Coordinate appointments between patients and psychologists
- **Reporting**: Provide comprehensive appointment reports with related entity information

**Key Challenges:**
1. Complex relational data model with 4 interconnected entities
2. Role-based account system (patient vs psychologist)
3. Conditional form fields based on user role
4. Data aggregation across multiple tables for reporting
5. RESTful API design aligned with Django best practices
6. Educational constraints (must follow Django tutorials 1-4)

# Assumptions

1. **Single Database**: PostgreSQL as the sole data persistence layer
2. **Monolithic Architecture**: Django monolith (not microservices) suitable for educational purposes
3. **Form-Based UI**: Traditional Django templates with forms (not SPA/REST API frontend)
4. **Synchronous Operations**: No async task queuing needed initially
5. **Basic Authentication**: No JWT/OAuth
6. **Single Language**: English
7. **Docker Development**: Local development via Docker Compose
8. **Tutorial Compliance**: Must demonstrate concepts from Django tutorials 1-4:
   - Project setup and apps
   - Models and migrations
   - Views and URL routing
   - Templates and forms
   - Admin interface

# Detailed Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Django Project                      │
│                (psychologist_system)                 │
├─────────────────────────────────────────────────────┤
│  Apps:                                               │
│  ├── accounts/     (User & Account Management)       │
│  ├── offices/      (Doctor's Office Management)      │
│  ├── doctors/      (Psychologist Profile Management) │
│  └── appointments/ (Appointment Scheduling)          │
├─────────────────────────────────────────────────────┤
│  Core Infrastructure:                                │
│  ├── config/settings/  (Environment-based config)    │
│  ├── templates/        (Shared templates)            │
│  ├── static/           (CSS/JS assets)               │
│  └── core/             (Shared utilities)            │
└─────────────────────────────────────────────────────┘
```

## Data Model Design (SOLID: Single Responsibility)

### 1. Account Model (`accounts.Account`)
**Responsibility**: Manage user identity and role

```python
class Account(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('psychologist', 'Psychologist'),
    ]
    
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'name']
        indexes = [
            models.Index(fields=['role', 'email']),
        ]
    
    def __str__(self):
        return f"{self.name} {self.last_name} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.name} {self.last_name}"
```

### 2. DoctorsOffice Model (`offices.DoctorsOffice`)
**Responsibility**: Manage office locations and contact information

```python
class DoctorsOffice(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    psychologist = models.ForeignKey(
        'accounts.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'psychologist'},
        related_name='managed_offices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Doctor's Office"
        verbose_name_plural = "Doctors' Offices"
    
    def __str__(self):
        return self.name
```

### 3. Doctor Model (`doctors.Doctor`)
**Responsibility**: Link psychologists to offices with specialty

```python
class Doctor(models.Model):
    SPECIALTY_CHOICES = [
        ('clinical', 'Clinical Psychology'),
        ('cognitive', 'Cognitive Psychology'),
        ('developmental', 'Developmental Psychology'),
        ('social', 'Social Psychology'),
        ('neuropsychology', 'Neuropsychology'),
        ('counseling', 'Counseling Psychology'),
    ]
    
    account = models.OneToOneField(
        'accounts.Account',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'psychologist'},
        related_name='doctor_profile'
    )
    doctors_office = models.ForeignKey(
        'offices.DoctorsOffice',
        on_delete=models.CASCADE,
        related_name='doctors'
    )
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['account__last_name', 'account__name']
    
    def __str__(self):
        return f"Dr. {self.account.get_full_name()} - {self.get_specialty_display()}"
```

### 4. Appointment Model (`appointments.Appointment`)
**Responsibility**: Manage appointment scheduling and status

```python
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='patient_appointments'
    )
    psychologist = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'psychologist'},
        related_name='psychologist_appointments'
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-time']
        unique_together = ['psychologist', 'date', 'time']
        indexes = [
            models.Index(fields=['date', 'psychologist']),
            models.Index(fields=['patient', 'status']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} with {self.psychologist.get_full_name()} on {self.date}"
```

## API Design (SOLID: Interface Segregation)

### API Endpoints

| Method | Endpoint | Purpose | View Type |
|--------|----------|---------|-----------|
| POST | `/api/accounts/create` | Create account | Function-based |
| POST | `/api/appointments/create` | Create appointment | Function-based |
| POST | `/api/doctors/create` | Create doctor profile | Function-based |
| POST | `/api/doctors-office/create` | Create office | Function-based |
| GET | `/api/appointment-report` | Appointment report | Function-based |

### API Response Structure (KISS: Keep It Simple)

**Success Response:**
```json
{
  "success": true,
  "message": "Resource created successfully",
  "data": {
    "id": 1,
    ...
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

## URL Structure (Django Tutorial 3)

```python
# Main urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('doctors/', include('doctors.urls')),
    path('offices/', include('offices.urls')),
    path('api/', include('api.urls')),
]

# api/urls.py
urlpatterns = [
    path('accounts/create', AccountCreateAPIView.as_view(), name='api-account-create'),
    path('appointments/create', AppointmentCreateAPIView.as_view(), name='api-appointment-create'),
    path('doctors/create', DoctorCreateAPIView.as_view(), name='api-doctor-create'),
    path('doctors_office/create', DoctorsOfficeCreateAPIView.as_view(), name='api-office-create'),
    path('appointment-report', AppointmentReportAPIView.as_view(), name='api-appointment-report'),
]
```

## View Layer (SOLID: Open/Closed Principle)

### Form Views with Templates

```python
# accounts/views.py
def create_account_view(request):
    """Render and handle account creation form"""
    if request.method == 'POST':
        # Handle form submission, call API
        pass
    else:
        form = AccountForm()
    return render(request, 'accounts/create.html', {'form': form})

# Dynamic form behavior via JavaScript
# When role=psychologist: show doctor_office and specialty dropdowns
```

### API Views (Business Logic)

```python
# api/views.py
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

class AccountCreateAPIView(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Create new account with validation"""
        try:
            # Parse and validate data
            # Create account
            # If psychologist with office/specialty: create doctor profile
            return JsonResponse({'success': True, ...})
        except ValidationError as e:
            return JsonResponse({'success': False, 'errors': e.message_dict}, status=400)
```

## Form Design (Django Tutorial 4)

### Account Form with Conditional Fields

```python
# accounts/forms.py
class AccountForm(forms.ModelForm):
    doctors_office = forms.ModelChoiceField(
        queryset=DoctorsOffice.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    specialty = forms.ChoiceField(
        choices=Doctor.SPECIALTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Account
        fields = ['name', 'last_name', 'age', 'gender', 'phone', 'email', 'role']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'psychologist':
            if not cleaned_data.get('doctors_office'):
                raise ValidationError("Doctor's office is required for psychologists")
            if not cleaned_data.get('specialty'):
                raise ValidationError("Specialty is required for psychologists")
        
        return cleaned_data
```

## Template Structure

```
templates/
├── base.html                    # Base template with navigation
├── 404.html                     # Custom 404 handler
├── accounts/
│   ├── create.html             # Account creation form
│   └── list.html               # Account listing
├── appointments/
│   ├── create.html             # Appointment form
│   ├── list.html               # Appointment list
│   └── report.html             # Appointment report table
├── doctors/
│   ├── create.html             # Doctor profile form
│   └── list.html               # Doctor listing
└── offices/
    ├── create.html             # Office form
    └── list.html               # Office listing
```

## Docker Configuration

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    env_file: .env
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - '5432:5432'
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    networks:
      - psychologist-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - psychologist-network

networks:
  psychologist-network:
    driver: bridge
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

# SOLID & KISS Considerations

## Single Responsibility Principle (SRP)
✅ **Applied:**
- Each model manages one entity type
- Separate apps for distinct domains (accounts, offices, doctors, appointments)
- Views handle presentation, models handle business logic
- Forms handle validation

## Open/Closed Principle (OCP)
✅ **Applied:**
- Models use Django's extensible base classes
- Views can be extended without modification
- Form validation is extensible via custom validators

## Liskov Substitution Principle (LSP)
✅ **Applied:**
- All views follow Django's view contract
- Forms follow Django's form interface
- Models follow Django ORM interface

## Interface Segregation Principle (ISP)
✅ **Applied:**
- Separate API endpoints for each operation (not one monolithic endpoint)
- Forms are specific to their use case (AccountForm, AppointmentForm, etc.)

## Dependency Inversion Principle (DIP)
✅ **Applied:**
- Views depend on model abstractions (Django ORM), not concrete implementations
- Database backend is configurable (PostgreSQL via settings)

## KISS Principle
✅ **Applied:**
- Function-based views for simplicity (not complex CBVs)
- Straightforward form handling
- Direct API responses without over-engineering
- Standard Django patterns without unnecessary abstractions

# Solution Plan (Step-by-Step)

## Phase 1: Project Setup
1. ✅ Create Django project structure
2. ✅ Configure PostgreSQL connection
3. ✅ Setup Docker environment
4. ✅ Create virtual environment
5. ✅ Configure settings for development

## Phase 2: Models & Database
1. ✅ Create `accounts` app with Account model
2. ✅ Create `offices` app with DoctorsOffice model
3. ✅ Create `doctors` app with Doctor model
4. ✅ Create `appointments` app with Appointment model
5. ✅ Run migrations
6. ✅ Configure admin interface for all models

## Phase 3: Forms
1. ✅ Create AccountForm with conditional fields
2. ✅ Create AppointmentForm with dropdowns
3. ✅ Create DoctorForm
4. ✅ Create DoctorsOfficeForm
5. ✅ Add form validation

## Phase 4: Views & URLs
1. ✅ Create form views for each entity
2. ✅ Create API views for each endpoint
3. ✅ Configure URL routing
4. ✅ Add dynamic URL parameters
5. ✅ Implement 404 handler

## Phase 5: Templates
1. ✅ Create base template with navigation
2. ✅ Create form templates for each entity
3. ✅ Create appointment report template
4. ✅ Add CSS styling
5. ✅ Implement JavaScript for conditional fields

## Phase 6: API Implementation
1. ✅ Implement `/api/accounts/create`
2. ✅ Implement `/api/appointments/create`
3. ✅ Implement `/api/doctors/create`
4. ✅ Implement `/api/doctors-office/create`
5. ✅ Implement `/api/appointment-report`

## Phase 7: Testing & Refinement
1. ✅ Test all forms
2. ✅ Test all API endpoints
3. ✅ Verify relationships and constraints
4. ✅ Test Docker setup
5. ✅ Documentation

# Drawbacks

## Implementation Complexity
- **Moderate complexity** due to 4 interconnected models
- Conditional form logic adds JavaScript dependency
- Relationship constraints require careful validation

## Educational Constraints
- Must avoid advanced Django features (DRF, async views, etc.)
- Limited to tutorial 1-4 concepts may feel restrictive
- Cannot use modern best practices (API-first, JWT, etc.)

## Scalability Limitations
- Form-based architecture doesn't scale to mobile/SPA
- Synchronous views may bottleneck under load
- No caching strategy defined
- No API versioning

## Maintenance Concerns
- Mixing form views and API views can be confusing
- Conditional form logic in templates is fragile
- No automated testing strategy defined

## Recommended Approach
**Option: Hybrid with Function-Based Views + Form Classes**
- Meets all educational requirements
- Follows Django tutorials 1-4
- Balances simplicity and functionality
- Room to grow (can add DRF later)
- Clear separation of concerns

# Adoption Strategy

## Migration Path
1. Start with minimal viable models
2. Build forms incrementally
3. Add API endpoints progressively
4. Polish UI last

## Breaking Changes
None - this is a new project

## Developer Onboarding
1. Read Django tutorials 1-4
2. Review this RFC
3. Setup local Docker environment
4. Run migrations and test data
5. Start with one app at a time

# How We Teach This

## Core Concepts Demonstrated

### Django Tutorial 1: Getting Started
- ✅ Project creation (`django-admin startproject`)
- ✅ App creation (`python manage.py startapp`)
- ✅ Settings configuration
- ✅ URL routing

### Django Tutorial 2: Models and Admin
- ✅ Model definition
- ✅ Migrations (`makemigrations`, `migrate`)
- ✅ Admin interface registration
- ✅ Model relationships (ForeignKey, OneToOneField)

### Django Tutorial 3: Views and URLs
- ✅ Function-based views
- ✅ URL patterns with `path()`
- ✅ Dynamic URLs with parameters
- ✅ Template rendering

### Django Tutorial 4: Forms
- ✅ ModelForms
- ✅ Form validation
- ✅ Form handling in views
- ✅ POST data processing

## Documentation Updates Needed
1. Create `README.md` with setup instructions
2. Document API endpoints with examples
3. Add inline code comments
4. Create `CONTRIBUTING.md` for future developers

## Teaching Approach
- Start with models (data-first)
- Build admin interface to visualize
- Create forms for data entry
- Add views to connect forms to models
- Implement templates for presentation
- Add API endpoints last

# Unresolved Questions

## Technical Questions
1. **Authentication**: Should we add Django's built-in authentication or keep it simple?
   - **Recommendation**: Skip for now (educational focus), add later if needed

2. **Validation**: How strict should phone/email validation be?
   - **Recommendation**: Basic Django validation, can enhance later

3. **Time Zones**: How to handle appointment time zones?
   - **Recommendation**: Use server timezone for simplicity

4. **Soft Deletes**: Should we implement soft deletes or hard deletes?
   - **Recommendation**: Hard deletes for simplicity

## Design Questions
1. **Multiple Offices per Psychologist**: Current design allows one. Should we support many?
   - **Recommendation**: Keep one-to-one for simplicity, refactor if needed

2. **Appointment Duration**: Should we store/validate appointment duration?
   - **Recommendation**: No, assume fixed duration (1 hour)

3. **Cancellation Reason**: Should we track why appointments are cancelled?
   - **Recommendation**: No, keep status simple

4. **Historical Data**: Should we keep appointment history after status change?
   - **Recommendation**: Yes, use `updated_at` field for audit trail

## Process Questions
1. **Testing Strategy**: Unit tests, integration tests, or manual testing?
   - **Recommendation**: Manual testing for educational project

2. **Code Review**: Required before implementation?
   - **Recommendation**: Yes, this RFC should be reviewed

3. **Deployment**: How/where to deploy for demo?
   - **Recommendation**: Local Docker only for now

---

**Next Steps:**
1. Review and approve this RFC
2. Setup project structure
3. Implement Phase 1 (Project Setup)
4. Iterate through phases 2-7

**Estimated Timeline:**
- Phase 1-2: 2-3 hours
- Phase 3-4: 3-4 hours
- Phase 5-6: 3-4 hours
- Phase 7: 1-2 hours
- **Total: 10-15 hours**
