"""Enhanced Django admin configuration for Account model.

Basic enhancements as per RFC-0002:
- Custom list displays with formatted dates
- Filters and search
- Better form layouts with inline editing for doctors
- Query optimization
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Account, Role
from doctors.models import Doctor


class DoctorInline(admin.StackedInline):
    """Inline admin for Doctor model when editing psychologist accounts.
    
    Only displays for accounts with role='psychologist'.
    Allows editing doctor profile without leaving account page.
    """
    model = Doctor
    extra = 0
    fields = ['doctors_office', 'specialty']
    can_delete = False
    verbose_name = "Doctor Profile"
    verbose_name_plural = "Doctor Profile"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Enhanced admin configuration for Account model.
    
    Features:
    - Custom list display with formatted data
    - Role and gender filters
    - Search by name, email, phone
    - Inline doctor profile editing for psychologists
    - Collapsible timestamp section
    - Query optimization with select_related
    """
    list_display = [
        'id',
        'get_full_name_display',
        'email',
        'role_badge',
        'gender_display',
        'age',
        'phone',
        'created_at_formatted'
    ]
    list_filter = ('role', 'gender', 'created_at')
    search_fields = ('name', 'last_name', 'email', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'last_name', 'age', 'gender')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Role', {
            'fields': ('role',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related to prevent N+1 queries."""
        queryset = super().get_queryset(request)
        return queryset.select_related('doctor_profile__doctors_office')
    
    def get_inline_instances(self, request, obj=None):
        """Only show doctor inline for psychologist accounts."""
        if obj and obj.role and obj.role.code == 'psychologist':
            return [DoctorInline(self.model, self.admin_site)]
        return []
    
    def get_full_name_display(self, obj):
        """Display full name with link to detail page."""
        return obj.get_full_name()
    get_full_name_display.short_description = 'Full Name'
    get_full_name_display.admin_order_field = 'last_name'
    
    def role_badge(self, obj):
        """Display role as colored badge."""
        colors = {
            'patient': '#2196F3',
            'psychologist': '#4CAF50',
            'supervisor': '#FF9800',
        }
        role_code = obj.role.code if obj.role else 'unknown'
        color = colors.get(role_code, '#757575')
        role_name = obj.role.name if obj.role else 'No Role'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, role_name
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role__name'
    
    def gender_display(self, obj):
        """Display gender with icon."""
        icons = {
            'M': '♂',
            'F': '♀',
            'O': '⚧',
        }
        icon = icons.get(obj.gender, '')
        return f"{icon} {obj.get_gender_display()}"
    gender_display.short_description = 'Gender'
    gender_display.admin_order_field = 'gender'
    
    def created_at_formatted(self, obj):
        """Format created_at timestamp."""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = 'Created'
    created_at_formatted.admin_order_field = 'created_at'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin configuration for Role model.
    
    Allows viewing and managing dynamic roles.
    """
    list_display = ['name', 'code', 'account_count', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['code', 'created_at']
    ordering = ['name']
    
    def account_count(self, obj):
        """Display count of accounts with this role."""
        return obj.accounts.count()
    account_count.short_description = 'Accounts'
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion if role has associated accounts."""
        if obj and obj.accounts.exists():
            return False
        return super().has_delete_permission(request, obj)
