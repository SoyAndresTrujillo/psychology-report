from django.contrib import admin
from .models import DoctorsOffice


@admin.register(DoctorsOffice)
class DoctorsOfficeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'psychologist', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'address', 'email', 'phone')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('psychologist',)
    
    fieldsets = (
        ('Office Information', {
            'fields': ('name', 'address')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Management', {
            'fields': ('psychologist',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
