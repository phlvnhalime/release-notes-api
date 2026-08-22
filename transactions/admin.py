from django.contrib import admin

from transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account",
        "transaction_type",
        "amount",
        "created_at",
    )
    search_fields = ("account__account_number", "description")
    list_filter = ("transaction_type",)
