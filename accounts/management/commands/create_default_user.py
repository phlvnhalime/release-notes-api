from decimal import Decimal

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Account, UserABS


class Command(BaseCommand):
    help = "Create default user and account from .env settings."

    def handle(self, *args, **options):
        email = settings.DEFAULT_USER_EMAIL
        password = settings.DEFAULT_USER_PASSWORD

        if not password:
            raise CommandError("DEFAULT_USER_PASSWORD is not set in .env")

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

        self.stdout.write(self.style.SUCCESS("Default user ready."))
        self.stdout.write(f"  Email:    {email}")
        self.stdout.write(f"  Password: {password}")
        self.stdout.write(f"  Account:  {account.account_number} ({account.account_type})")
        self.stdout.write(f"  Balance:  {account.balance}")

        if not user_created:
            self.stdout.write("  UserABS already existed — password updated from .env.")
        if not account_created:
            self.stdout.write("  Account already existed.")
