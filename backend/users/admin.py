from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id', 'email', 'username',
        'first_name', 'last_name', 'is_staff'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('id',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
