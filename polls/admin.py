from django.contrib import admin
from .models import Polls 


@admin.register(Polls)
class PollsAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'rate', 'created_at')
    list_filter = ('rate', 'created_at')
    search_fields = ('description',)
    ordering = ('rate', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Poll', {
            'fields': ('description', 'rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
