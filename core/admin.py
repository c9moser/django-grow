from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'id', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username', 'id', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = BaseUserAdmin.fieldsets + (
    )
    ordering = ('email',)
