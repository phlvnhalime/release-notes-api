from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.db import migrations

DEFAULT_EMAIL = "admin@example.com"
DEFAULT_PASSWORD = "default_password"


def pre_default_init(apps, schema_editor):
    UserABS = apps.get_model("accounts", "UserABS")
    Account = apps.get_model("accounts", "Account")

    user, created = UserABS.objects.get_or_create(
        email=DEFAULT_EMAIL,
        defaults={
            "first_name": "default_user",
            "last_name": "",
            "password": make_password(DEFAULT_PASSWORD),
            "is_active": True,
        },
    )
    if not created:
        user.password = make_password(DEFAULT_PASSWORD)
        user.save(update_fields=["password"])

    Account.objects.get_or_create(
        user=user,
        account_number="1234567890",
        defaults={
            "account_type": "checking",
            "balance": Decimal("1000.00"),
        },
    )


def post_default_init(apps, schema_editor):
    UserABS = apps.get_model("accounts", "UserABS")
    Account = apps.get_model("accounts", "Account")

    Account.objects.filter(user__email=DEFAULT_EMAIL).delete()
    UserABS.objects.filter(email=DEFAULT_EMAIL).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(pre_default_init, post_default_init),
    ]
