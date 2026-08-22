from decimal import Decimal, InvalidOperation

from django.db import transaction as db_transaction
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.account_views import get_user_account
from accounts.models import Account
from transactions.models import Transaction
from transactions.utils import ALLOWED_TYPES, filter_transactions


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

    def get(self, request, account_uuid):
        account = get_user_account(request.user, account_uuid)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)

        rows = Transaction.objects.filter(
            account=account,
            deleted_at__isnull=True,
        )
        rows, error = filter_transactions(rows, request.query_params)
        if error:
            return Response({"__detail__": error}, status=400)
        rows = rows.order_by("-created_at")
        return Response([row.to_dict() for row in rows])

    def post(self, request, account_uuid):
        transaction_type = request.data.get("transaction_type")
        amount = parse_amount(request.data.get("amount"))
        description = request.data.get("description") or ""

        if transaction_type not in ALLOWED_TYPES or amount is None:
            return Response({"__detail__": "__fields_required__"}, status=400)

        with db_transaction.atomic():
            account = (
                Account.objects.select_for_update()
                .filter(
                    uuid=account_uuid,
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

    def get(self, request, account_uuid, transaction_uuid):
        account = get_user_account(request.user, account_uuid)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)

        row = Transaction.objects.filter(
            uuid=transaction_uuid,
            account=account,
            deleted_at__isnull=True,
        ).first()
        if row is None:
            return Response({"__detail__": "__not_found__"}, status=404)
        return Response(row.to_dict())

    def delete(self, request, account_uuid, transaction_uuid):
        with db_transaction.atomic():
            account = (
                Account.objects.select_for_update()
                .filter(
                    uuid=account_uuid,
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
                    uuid=transaction_uuid,
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


class AccountSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_uuid):
        account = get_user_account(request.user, account_uuid)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)

        rows = Transaction.objects.filter(
            account=account,
            deleted_at__isnull=True,
        )
        rows, error = filter_transactions(rows, request.query_params)
        if error:
            return Response({"__detail__": error}, status=400)

        totals = rows.aggregate(
            income_total=Coalesce(
                Sum(
                    "amount",
                    filter=Q(transaction_type=Transaction.INCOME),
                ),
                Decimal("0.00"),
            ),
            expense_total=Coalesce(
                Sum(
                    "amount",
                    filter=Q(transaction_type=Transaction.EXPENSE),
                ),
                Decimal("0.00"),
            ),
        )
        income_total = totals["income_total"]
        expense_total = totals["expense_total"]

        return Response(
            {
                "__account_id__": account.id,
                "__uuid__": str(account.uuid),
                "__balance__": str(account.balance),
                "__income_total__": str(income_total),
                "__expense_total__": str(expense_total),
                "__count__": rows.count(),
            }
        )
