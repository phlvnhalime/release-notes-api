from django.urls import path

from transactions.views import TransactionDetailView, TransactionListCreateView

urlpatterns = [
    path(
        "accounts/<int:account_id>/transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "accounts/<int:account_id>/transactions/<int:transaction_id>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
]
