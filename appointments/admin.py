"""Enhanced Django admin configuration for Appointment model.

Basic enhancements as per RFC-0002:
- Custom list displays with status badges
- Filters and search
- Custom admin actions
- Query optimization
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Enhanced admin configuration for Appointment model.
    
    Features:
    - Custom list display with colored status badges
    - Status and date filters
    - Search by patient and psychologist names
    - Custom admin actions (mark as completed/cancelled)
    - Query optimization with select_related
    - Date hierarchy navigation
    """
    list_display = [
        'id',
        'patient_name',
        'psychologist_name',
        'date',
        'time',
        'status_badge',
        'created_at_formatted'
    ]
    list_filter = ('status', 'date', 'created_at')
    search_fields = (
        'patient__name',
        'patient__last_name',
        'patient__email',
        'psychologist__name',
        'psychologist__last_name',
        'psychologist__email'
    )
    ordering = ('-date', '-time')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient', 'psychologist')
    date_hierarchy = 'date'
    list_per_page = 25
    actions = ['mark_as_completed', 'mark_as_cancelled', 'mark_as_confirmed']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'psychologist', 'date', 'time')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related to prevent N+1 queries."""
        queryset = super().get_queryset(request)
        return queryset.select_related('patient', 'psychologist')
    
    def patient_name(self, obj):
        """Display patient full name."""
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__last_name'
    
    def psychologist_name(self, obj):
        """Display psychologist full name."""
        return obj.psychologist.get_full_name()
    psychologist_name.short_description = 'Psychologist'
    psychologist_name.admin_order_field = 'psychologist__last_name'
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'scheduled': '#2196F3',
            'confirmed': '#FF9800',
            'completed': '#4CAF50',
            'cancelled': '#F44336',
            'no_show': '#757575',
        }
        color = colors.get(obj.status, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def created_at_formatted(self, obj):
        """Format created_at timestamp."""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = 'Created'
    created_at_formatted.admin_order_field = 'created_at'
    
    # Admin Actions
    @admin.action(description='Mark selected appointments as completed')
    def mark_as_completed(self, request, queryset):
        """Bulk action to mark appointments as completed."""
        updated = queryset.update(status='completed')
        self.message_user(
            request,
            f'{updated} appointment(s) marked as completed.'
        )
    
    @admin.action(description='Mark selected appointments as cancelled')
    def mark_as_cancelled(self, request, queryset):
        """Bulk action to mark appointments as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(
            request,
            f'{updated} appointment(s) marked as cancelled.'
        )
    
    @admin.action(description='Mark selected appointments as confirmed')
    def mark_as_confirmed(self, request, queryset):
        """Bulk action to mark appointments as confirmed."""
        updated = queryset.update(status='confirmed')
        self.message_user(
            request,
            f'{updated} appointment(s) marked as confirmed.'
        )
