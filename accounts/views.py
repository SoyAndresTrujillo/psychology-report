from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Account
from .forms import AccountForm
from doctors.models import Doctor


def home_view(request):
    """Home page with navigation to all sections.
    
    Technical Details:
    - Simple template rendering view
    - No database queries
    - Serves as entry point for the application
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered home.html template
    """
    return render(request, 'home.html')


def create_account_view(request):
    """Create a new account (patient or psychologist).
    
    Technical Details:
    - Handles POST requests for account creation via AccountForm
    - Performs conditional doctor profile creation for psychologists
    - Uses Django's form validation pipeline (clean methods)
    - Implements atomic operation: account creation + optional doctor profile
    - Redirects to accounts list on success with flash message
    
    Form Validation:
    - AccountForm.clean_email(): Ensures email uniqueness
    - AccountForm.clean_age(): Validates age range (1-120)
    - AccountForm.clean(): Validates psychologist conditional fields
    
    Database Operations:
    - Creates Account instance via form.save()
    - Creates Doctor instance if role == 'psychologist'
    - Links Doctor to Account via OneToOneField relationship
    
    Args:
        request: HttpRequest object containing POST data or GET request
        
    Returns:
        HttpResponse: Rendered create form or redirect to accounts:list
    """
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            
            # If psychologist, create doctor profile
            if account.role == 'psychologist':
                doctors_office = form.cleaned_data.get('doctors_office')
                specialty = form.cleaned_data.get('specialty')
                
                Doctor.objects.create(
                    account=account,
                    doctors_office=doctors_office,
                    specialty=specialty
                )
            
            messages.success(request, f'Account created successfully for {account.get_full_name()}!')
            return redirect('accounts:list')
    else:
        form = AccountForm()
    
    return render(request, 'accounts/create.html', {'form': form})


def list_accounts_view(request):
    """List all accounts with statistics.
    
    Technical Details:
    - Retrieves all Account objects ordered by creation date (descending)
    - Performs aggregate queries for role-based counts
    - Uses Django ORM filter() for conditional counting
    - No pagination implemented (consider for large datasets)
    
    Database Queries:
    - SELECT * FROM accounts ORDER BY created_at DESC
    - COUNT queries for role filtering (patients/psychologists)
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered list template with accounts and statistics
    """
    accounts = Account.objects.all().order_by('-created_at')
    context = {
        'accounts': accounts,
        'total_count': accounts.count(),
        'patients_count': accounts.filter(role='patient').count(),
        'psychologists_count': accounts.filter(role='psychologist').count(),
    }
    return render(request, 'accounts/list.html', context)


def account_detail_view(request, account_id):
    """View detailed account information with optional doctor profile.
    
    Technical Details:
    - Uses get_object_or_404 for safe object retrieval (raises Http404)
    - Handles OneToOneField relationship with Doctor model
    - Gracefully handles missing doctor profiles via try/except
    - Uses related_name='doctor_profile' from Doctor.account field
    
    Database Queries:
    - SELECT * FROM accounts WHERE id = account_id
    - SELECT * FROM doctors WHERE account_id = account_id (if psychologist)
    
    Args:
        request: HttpRequest object
        account_id: Integer primary key of the Account to retrieve
        
    Returns:
        HttpResponse: Rendered detail template with account and doctor_profile
        
    Raises:
        Http404: If account with given ID does not exist
    """
    account = get_object_or_404(Account, id=account_id)
    doctor_profile = None
    
    if account.role == 'psychologist':
        try:
            doctor_profile = account.doctor_profile
        except Doctor.DoesNotExist:
            pass
    
    context = {
        'account': account,
        'doctor_profile': doctor_profile,
    }
    return render(request, 'accounts/detail.html', context)
