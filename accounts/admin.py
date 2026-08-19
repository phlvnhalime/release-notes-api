from django.contrib import admin

from accounts.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "user", "account_type", "balance", "created_at")
    search_fields = ("account_number", "user__email")
