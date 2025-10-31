from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'email', 'role', 'age', 'phone', 'created_at')
    list_filter = ('role', 'gender', 'created_at')
    search_fields = ('name', 'last_name', 'email', 'phone')
    ordering = ('last_name', 'name')
    readonly_fields = ('created_at', 'updated_at')
    
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
