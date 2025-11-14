"""Appointment views using Django generic class-based views.

Follows the same patterns as accounts app with:
- ListView for appointment list and report views
- CreateView for appointment creation
- Query optimization with select_related()
- Statistics and pagination
"""
import logging
from django.views.generic import ListView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from .models import Appointment
from .forms import AppointmentForm

logger = logging.getLogger(__name__)


class AppointmentStatsMixin:
    """Mixin to add appointment statistics to context."""
    
    def get_context_data(self, **kwargs):
        """Add appointment statistics to context."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        context['total_count'] = queryset.count()
        context['scheduled_count'] = queryset.filter(status='scheduled').count()
        context['confirmed_count'] = queryset.filter(status='confirmed').count()
        context['completed_count'] = queryset.filter(status='completed').count()
        context['cancelled_count'] = queryset.filter(status='cancelled').count()
        
        return context


class AppointmentListView(AppointmentStatsMixin, ListView):
    """List all appointments with pagination and statistics.
    
    Features:
    - Pagination (20 items per page)
    - Query optimization with select_related()
    - Status-based statistics
    - Ordered by date and time (descending)
    
    URL: /appointments/
    Template: appointments/list.html
    Context: appointments, page_obj, is_paginated, *_count statistics
    """
    model = Appointment
    template_name = 'appointments/list.html'
    context_object_name = 'appointments'
    paginate_by = 20
    ordering = ['-date', '-time']
    
    def get_queryset(self):
        """Optimize query to prevent N+1 queries.
        
        Uses select_related for patient and psychologist foreign keys.
        """
        return super().get_queryset().select_related(
            'patient',
            'psychologist'
        )


class AppointmentCreateView(SuccessMessageMixin, CreateView):
    """Create new appointment.
    
    CreateView handles:
    - Form rendering (GET)
    - Form validation and saving (POST)
    - Success message display
    - Redirect on success
    
    URL: /appointments/create/
    Template: appointments/create.html
    Context: form
    Success URL: /appointments/
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/create.html'
    success_url = reverse_lazy('appointments:list')
    success_message = "Appointment created successfully for %(date)s at %(time)s!"
    
    def form_valid(self, form):
        """Handle successful form submission.
        
        Future enhancement: Could add MongoDB sync here similar to accounts.
        """
        response = super().form_valid(form)
        appointment = self.object
        
        logger.info(
            f"Appointment {appointment.id} created: "
            f"Patient {appointment.patient.id} with "
            f"Psychologist {appointment.psychologist.id}"
        )
        
        return response


class AppointmentReportView(ListView):
    """Generate detailed appointment report.
    
    Similar to AppointmentListView but with:
    - No pagination (full report)
    - Deep select_related for doctor and office info
    - Different template for report formatting
    
    URL: /appointments/report/
    Template: appointments/report.html
    Context: appointments
    """
    model = Appointment
    template_name = 'appointments/report.html'
    context_object_name = 'appointments'
    ordering = ['-date', '-time']
    
    def get_queryset(self):
        """Optimize query with deep select_related for full report data.
        
        Includes patient, psychologist, doctor profile, and office info
        to avoid multiple queries when rendering report.
        """
        return super().get_queryset().select_related(
            'patient',
            'psychologist',
            'psychologist__doctor_profile__doctors_office'
        )
