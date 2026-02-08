from django.contrib import admin
from .models import Athlete


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nickname', 'organization', 'weight', 'height', 'age', 'country', 'team', 'created_at')
    list_filter = ('organization', 'country', 'team', 'created_at')
    search_fields = ('first_name', 'last_name', 'nickname', 'organization', 'country', 'team')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'nickname', 'age', 'country')
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'height')
        }),
        ('Organization', {
            'fields': ('organization', 'team')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
