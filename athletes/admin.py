from django.contrib import admin
from .models import Athlete


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'organization', 'created_at')
    list_filter = ('organization', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'organization')
    readonly_fields = ('created_at',)
