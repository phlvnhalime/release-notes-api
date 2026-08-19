from django.core.management.base import BaseCommand, CommandError

from accounts.toolbox.sync_default_user import sync_default_user


class Command(BaseCommand):
    help = "Create default user and account from .env settings."

    def handle(self, *args, **options):
        try:
            result = sync_default_user()
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS("Default user ready."))
        self.stdout.write(f"  Email:    {result['email']}")
        self.stdout.write(f"  Password: {result['password']}")
        self.stdout.write(
            f"  Account:  {result['account'].account_number} ({result['account'].account_type})"
        )
        self.stdout.write(f"  Balance:  {result['account'].balance}")

        if not result["user_created"]:
            self.stdout.write("  UserABS already existed — password updated from .env.")
        if not result["account_created"]:
            self.stdout.write("  Account already existed.")
