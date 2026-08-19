from decimal import Decimal

from django.conf import settings
from django.contrib.auth.hashers import make_password

from accounts.models import Account, UserABS


def sync_default_user():
    email = settings.DEFAULT_USER_EMAIL
    password = settings.DEFAULT_USER_PASSWORD

    if not email:
        raise ValueError("DEFAULT_USER_EMAIL is not set in .env")
    if not password:
        raise ValueError("DEFAULT_USER_PASSWORD is not set in .env")

    hashed_password = make_password(password)

    user_abs, user_created = UserABS.objects.get_or_create(
        email=email,
        defaults={
            "first_name": settings.DEFAULT_USER_FIRST_NAME,
            "last_name": settings.DEFAULT_USER_LAST_NAME,
            "password": hashed_password,
            "is_active": True,
        },
    )
    if not user_created:
        user_abs.password = hashed_password
        user_abs.is_active = True
        user_abs.save(update_fields=["password", "is_active"])

    account, account_created = Account.objects.get_or_create(
        user=user_abs,
        account_number=settings.DEFAULT_ACCOUNT_NUMBER,
        defaults={
            "account_type": settings.DEFAULT_ACCOUNT_TYPE,
            "balance": Decimal(str(settings.DEFAULT_ACCOUNT_BALANCE)),
        },
    )

    return {
        "email": email,
        "password": password,
        "user_abs": user_abs,
        "user_created": user_created,
        "account": account,
        "account_created": account_created,
    }
