from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'organization', 'created_at')
    list_filter = ('organization', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'organization')
    readonly_fields = ('created_at',)
