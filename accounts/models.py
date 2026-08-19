from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class UserABS(AbstractBaseUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
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
            "__id__": self.id,
            "__uuid__": str(self.uuid),
            "__email__": self.email,
            "__first_name__": self.first_name,
            "__last_name__": self.last_name,
            "__created_at__": self.created_at.isoformat(),
            "__updated_at__": self.updated_at.isoformat(),
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
            "__id__": self.id,
            "__uuid__": str(self.uuid),
            "__user__": self.user.to_dict(),
            "__account_number__": self.account_number,
            "__account_type__": self.account_type,
            "__balance__": str(self.balance),
            "__created_at__": self.created_at.isoformat(),
            "__updated_at__": self.updated_at.isoformat(),
        }
