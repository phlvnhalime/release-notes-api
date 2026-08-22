from decimal import Decimal, InvalidOperation

from django.db import transaction as db_transaction
from django.db.models import F
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.account_views import get_user_account
from accounts.models import Account
from transactions.models import Transaction

ALLOWED_TYPES = {Transaction.INCOME, Transaction.EXPENSE}


def parse_amount(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None
    if amount <= 0:
        return None
    return amount


class TransactionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_id):
        account = get_user_account(request.user, account_id)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)

        rows = Transaction.objects.filter(
            account=account,
            deleted_at__isnull=True,
        ).order_by("-created_at")
        return Response([row.to_dict() for row in rows])

    def post(self, request, account_id):
        transaction_type = request.data.get("transaction_type")
        amount = parse_amount(request.data.get("amount"))
        description = request.data.get("description") or ""

        if transaction_type not in ALLOWED_TYPES or amount is None:
            return Response({"__detail__": "__fields_required__"}, status=400)

        with db_transaction.atomic():
            account = (
                Account.objects.select_for_update()
                .filter(
                    pk=account_id,
                    user=request.user,
                    deleted_at__isnull=True,
                )
                .first()
            )
            if account is None:
                return Response({"__detail__": "__not_found__"}, status=404)

            if (
                transaction_type == Transaction.EXPENSE
                and account.balance < amount
            ):
                return Response(
                    {"__detail__": "__insufficient_balance__"},
                    status=400,
                )

            if transaction_type == Transaction.INCOME:
                account.balance = F("balance") + amount
            else:
                account.balance = F("balance") - amount
            account.save(update_fields=["balance", "updated_at"])

            row = Transaction.objects.create(
                account=account,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
            )

        return Response(row.to_dict(), status=201)


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_id, transaction_id):
        account = get_user_account(request.user, account_id)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)

        row = Transaction.objects.filter(
            pk=transaction_id,
            account=account,
            deleted_at__isnull=True,
        ).first()
        if row is None:
            return Response({"__detail__": "__not_found__"}, status=404)
        return Response(row.to_dict())

    def delete(self, request, account_id, transaction_id):
        with db_transaction.atomic():
            account = (
                Account.objects.select_for_update()
                .filter(
                    pk=account_id,
                    user=request.user,
                    deleted_at__isnull=True,
                )
                .first()
            )
            if account is None:
                return Response({"__detail__": "__not_found__"}, status=404)

            row = (
                Transaction.objects.select_for_update()
                .filter(
                    pk=transaction_id,
                    account=account,
                    deleted_at__isnull=True,
                )
                .first()
            )
            if row is None:
                return Response({"__detail__": "__not_found__"}, status=404)

            if row.transaction_type == Transaction.INCOME:
                if account.balance < row.amount:
                    return Response(
                        {"__detail__": "__insufficient_balance__"},
                        status=400,
                    )
                account.balance = F("balance") - row.amount
            else:
                account.balance = F("balance") + row.amount
            account.save(update_fields=["balance", "updated_at"])

            row.deleted_at = timezone.now()
            row.save(update_fields=["deleted_at", "updated_at"])

        return Response({"__detail__": "__deleted__"})
