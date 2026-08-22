from uuid import uuid4

from django.db import models

from accounts.models import Account


class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "transactions"

    def __str__(self):
        return f"{self.transaction_type} {self.amount}"

    def to_dict(self):
        return {
            "__id__": self.id,
            "__uuid__": str(self.uuid),
            "__account_id__": self.account_id,
            "__transaction_type__": self.transaction_type,
            "__amount__": str(self.amount),
            "__description__": self.description,
            "__created_at__": self.created_at.isoformat(),
            "__updated_at__": self.updated_at.isoformat(),
        }
