from uuid import uuid4

from django.db import models


class UserABS(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_abs"

    def __str__(self):
        return self.email

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Account(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    user = models.ForeignKey(
        UserABS,
        on_delete=models.CASCADE,
        related_name="accounts",
    )

    account_number = models.CharField(max_length=10, unique=True)
    account_type = models.CharField(max_length=10)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return self.account_number

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "user": self.user.to_dict(),
            "account_number": self.account_number,
            "account_type": self.account_type,
            "balance": str(self.balance),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
