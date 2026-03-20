from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'phone_number', 'is_installer', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_installer', 'is_active')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra', {'fields': ('phone_number', 'is_installer')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Extra', {'fields': ('email', 'phone_number', 'is_installer')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'address_type', 'city', 'is_default')
    list_filter = ('address_type', 'is_default')
    search_fields = ('user__email', 'city', 'postal_code')
