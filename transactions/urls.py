from django.urls import path

from transactions.views import (
    AccountSummaryView,
    TransactionDetailView,
    TransactionListCreateView,
)

urlpatterns = [
    path(
        "accounts/<account-uuid:account_uuid>/summary",
        AccountSummaryView.as_view(),
        name="account-summary",
    ),
    path(
        "accounts/<account-uuid:account_uuid>/transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "accounts/<account-uuid:account_uuid>/transactions/"
        "<transaction-uuid:transaction_uuid>",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
]
