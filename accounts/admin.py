from django.contrib import admin

from accounts.models import Account, UserABS


@admin.register(UserABS)
class UserABSAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_active", "created_at")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("password",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "user", "account_type", "balance", "created_at")
    search_fields = ("account_number", "user__email")
