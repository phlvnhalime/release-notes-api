from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account


def get_user_account(user, account_uuid):
    return Account.objects.filter(
        uuid=account_uuid,
        user=user,
        deleted_at__isnull=True,
    ).first()


class AccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = Account.objects.filter(
            user=request.user,
            deleted_at__isnull=True,
        )
        return Response([account.to_dict() for account in accounts])

    def post(self, request):
        account_number = request.data.get("account_number")
        account_type = request.data.get("account_type")

        if not account_number or not account_type:
            return Response({"__detail__": "__fields_required__"}, status=400)

        if Account.objects.filter(
            account_number=account_number,
            deleted_at__isnull=True,
        ).exists():
            return Response(
                {"__detail__": "__account_number_exists__"},
                status=400,
            )

        account = Account.objects.create(
            user=request.user,
            account_number=account_number,
            account_type=account_type,
        )
        return Response(account.to_dict(), status=201)


class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_uuid):
        account = get_user_account(request.user, account_uuid)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)
        return Response(account.to_dict())

    def patch(self, request, account_uuid):
        account = get_user_account(request.user, account_uuid)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)

        account_type = request.data.get("account_type")
        if not account_type:
            return Response({"__detail__": "__fields_required__"}, status=400)

        account.account_type = account_type
        account.save(update_fields=["account_type", "updated_at"])
        return Response(account.to_dict())

    def delete(self, request, account_uuid):
        account = get_user_account(request.user, account_uuid)
        if account is None:
            return Response({"__detail__": "__not_found__"}, status=404)

        account.deleted_at = timezone.now()
        account.save(update_fields=["deleted_at", "updated_at"])
        return Response({"__detail__": "__deleted__"})
