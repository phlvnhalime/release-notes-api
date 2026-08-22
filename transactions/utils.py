from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date

from transactions.models import Transaction

ALLOWED_TYPES = {Transaction.INCOME, Transaction.EXPENSE}


def parse_bound(value, end=False):
    day = parse_date(value)
    if day is None:
        return None
    bound = datetime.combine(day, time.max if end else time.min)
    if timezone.is_naive(bound):
        bound = timezone.make_aware(bound)
    return bound


def filter_transactions(queryset, query_params):
    transaction_type = query_params.get("transaction_type")
    if transaction_type:
        if transaction_type not in ALLOWED_TYPES:
            return None, "__invalid_transaction_type__"
        queryset = queryset.filter(transaction_type=transaction_type)

    date_from = query_params.get("date_from")
    if date_from:
        start = parse_bound(date_from)
        if start is None:
            return None, "__invalid_date__"
        queryset = queryset.filter(created_at__gte=start)

    date_to = query_params.get("date_to")
    if date_to:
        end = parse_bound(date_to, end=True)
        if end is None:
            return None, "__invalid_date__"
        queryset = queryset.filter(created_at__lte=end)

    return queryset, None
