from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'doctors_office', 'specialty', 'created_at')
    list_filter = ('specialty', 'created_at')
    search_fields = ('account__name', 'account__last_name', 'doctors_office__name')
    ordering = ('account__last_name', 'account__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('account', 'doctors_office')
    
    fieldsets = (
        ('Doctor Profile', {
            'fields': ('account', 'doctors_office', 'specialty')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
