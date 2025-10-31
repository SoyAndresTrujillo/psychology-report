from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'psychologist', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('patient__name', 'patient__last_name', 'psychologist__name', 'psychologist__last_name')
    ordering = ('-date', '-time')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient', 'psychologist')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'psychologist', 'date', 'time', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
