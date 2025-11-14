"""Account views using Django generic class-based views.

Follows Django best practices with generic views for common patterns:
- TemplateView for simple template rendering
- ListView for displaying list of objects with pagination
- DetailView for displaying single object details
- CreateView for object creation with forms

Integrates MongoDB dual-database pattern for account creation.
"""
import logging
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Account, Role
from .forms import AccountForm, RoleForm
from doctors.models import Doctor
from core.mongodb import mongo_service

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Home page with navigation to all sections.
    
    Uses TemplateView for simple template rendering without database queries.
    Follows Single Responsibility Principle - only renders template.
    """
    template_name = 'home.html'


class SearchMixin:
    """Mixin to add search functionality to list views.
    
    Provides reusable search capability across multiple model list views.
    Follows DRY principle by centralizing search logic.
    """
    search_fields = []
    
    def get_queryset(self):
        """Filter queryset based on search query parameter."""
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(q_objects)
        
        return queryset


class StatsMixin:
    """Mixin to add statistics to list view context.
    
    Provides aggregate statistics for list views.
    Can be composed with other mixins following composition over inheritance.
    """
    def get_context_data(self, **kwargs):
        """Add statistics to context data."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        context['total_count'] = queryset.count()
        # Get role instances for filtering
        try:
            patient_role = Role.objects.get(code='patient')
            psychologist_role = Role.objects.get(code='psychologist')
            context['patients_count'] = queryset.filter(role=patient_role).count()
            context['psychologists_count'] = queryset.filter(role=psychologist_role).count()
        except Role.DoesNotExist:
            context['patients_count'] = 0
            context['psychologists_count'] = 0
        
        return context

class AccountListView(SearchMixin, StatsMixin, ListView):
    """List all accounts with pagination, search, and statistics.
    
    Generic ListView eliminates boilerplate code for list display.
    Combines SearchMixin and StatsMixin for enhanced functionality.
    
    Features:
    - Pagination (20 items per page)
    - Search by name, last_name, or email
    - Query optimization with select_related for doctor profiles
    - Role-based statistics
    
    URL: /accounts/
    Template: accounts/list.html
    Context: accounts, page_obj, is_paginated, total_count, patients_count, psychologists_count
    """
    model = Account
    template_name = 'accounts/list.html'
    context_object_name = 'accounts'
    paginate_by = 20
    ordering = ['-created_at']
    search_fields = ['name', 'last_name', 'email']
    
    def get_queryset(self):
        """Optimize query with select_related to prevent N+1 queries."""
        queryset = super().get_queryset()
        return queryset.select_related('doctor_profile__doctors_office')


class AccountDetailView(DetailView):
    """Display detailed account information with optional doctor profile.
    
    DetailView automatically handles:
    - Object retrieval with pk from URL
    - Http404 if object doesn't exist
    - Context variable naming (account)
    
    URL: /accounts/<int:pk>/
    Template: accounts/detail.html
    Context: account, doctor_profile
    """
    model = Account
    template_name = 'accounts/detail.html'
    context_object_name = 'account'
    
    def get_queryset(self):
        """Optimize query with select_related for doctor profile."""
        return super().get_queryset().select_related('doctor_profile__doctors_office')
    
    def get_context_data(self, **kwargs):
        """Add doctor profile to context if account is psychologist."""
        context = super().get_context_data(**kwargs)
        account = self.object
        doctor_profile = None
        
        if account.role and account.role.code == 'psychologist':
            try:
                doctor_profile = account.doctor_profile
            except Doctor.DoesNotExist:
                logger.warning(f"Psychologist account {account.id} missing doctor profile")
        
        context['doctor_profile'] = doctor_profile
        return context


class AccountCreateView(SuccessMessageMixin, CreateView):
    """Create new account with MongoDB dual-database integration.
    
    CreateView handles:
    - Form rendering (GET)
    - Form validation and saving (POST)
    - Success message display
    - Redirect on success
    
    Dual-Database Pattern:
    1. Save to Django ORM (PostgreSQL) - primary database
    2. Save to MongoDB - secondary analytics database
    3. Create doctor profile if psychologist role
    
    URL: /accounts/create/
    Template: accounts/create.html
    Context: form
    Success URL: /accounts/
    """
    model = Account
    form_class = AccountForm
    template_name = 'accounts/create.html'
    success_url = reverse_lazy('accounts:list')
    success_message = "Account created successfully for %(name)s %(last_name)s!"
    
    def form_valid(self, form):
        """Handle successful form submission with dual-database write.
        
        Process:
        1. Save account to Django ORM
        2. Create doctor profile if psychologist
        3. Sync to MongoDB (non-blocking)
        4. Return success response
        
        MongoDB sync failures are logged but don't fail the request.
        This ensures Django ORM remains source of truth.
        """
        # Save to Django ORM (primary database)
        response = super().form_valid(form)
        account = self.object
        
        # Create doctor profile for psychologists
        if account.role and account.role.code == 'psychologist':
            doctors_office = form.cleaned_data.get('doctors_office')
            specialty = form.cleaned_data.get('specialty')
            
            try:
                Doctor.objects.create(
                    account=account,
                    doctors_office=doctors_office,
                    specialty=specialty
                )
                logger.info(f"Doctor profile created for account {account.id}")
            except Exception as e:
                logger.error(f"Failed to create doctor profile: {e}")
        
        # Sync to MongoDB (secondary database)
        try:
            success = mongo_service.save_account(account)
            if success:
                logger.info(f"Account {account.id} synced to MongoDB")
            else:
                logger.warning(f"Account {account.id} not synced to MongoDB")
        except Exception as e:
            # MongoDB failures should not break the request
            logger.error(f"MongoDB sync failed for account {account.id}: {e}")
        
        return response

class RoleCreateView(SuccessMessageMixin, CreateView):
    """Create new role and redirect to account creation.
    
    CreateView handles:
    - Form rendering (GET)
    - Form validation and saving (POST)
    - Success message display
    - Redirect to account creation
    
    URL: /accounts/create_role/
    Template: roles/create.html
    Context: form
    Success URL: /accounts/create/
    """
    model = Role
    form_class = RoleForm
    template_name = 'roles/create.html'
    success_url = reverse_lazy('accounts:create')
    success_message = "Role '%(name)s' created successfully! You can now use it when creating accounts."
    
    def form_valid(self, form):
        """Save the new role to database.
        
        Process:
        1. Save role to Django ORM (code is auto-generated from name)
        2. Log the creation
        3. Redirect to account creation form
        """
        response = super().form_valid(form)
        role = self.object
        logger.info(f"New role created: {role.name} (code: {role.code})")
        return response


