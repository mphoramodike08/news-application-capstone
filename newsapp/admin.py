"""Admin registrations for the news application models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article, CustomUser, Newsletter, Publisher


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Show the custom role field in the Django admin user editor."""

    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)


admin.site.register(Publisher)
admin.site.register(Newsletter)
admin.site.register(Article)
