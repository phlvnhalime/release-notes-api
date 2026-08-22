from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.models import Account, UserABS
from transactions.models import Transaction


@pytest.fixture
def user(db):
    user = UserABS(
        email="test@wallet.local",
        first_name="Test",
        last_name="User",
    )
    user.set_password("TestPass123!")
    user.save()
    return user


@pytest.fixture
def other_user(db):
    user = UserABS(
        email="other@wallet.local",
        first_name="Other",
        last_name="User",
    )
    user.set_password("OtherPass123!")
    user.save()
    return user


@pytest.fixture
def auth_client(client, user):
    client.post(
        "/api/auth/login/",
        {"email": "test@wallet.local", "password": "TestPass123!"},
        content_type="application/json",
    )
    return client


@pytest.fixture
def account(user):
    return Account.objects.create(
        user=user,
        account_number="9876543210",
        account_type="checking",
        balance="200.00",
    )


def _create_row(account, transaction_type, amount, created_at):
    row = Transaction.objects.create(
        account=account,
        transaction_type=transaction_type,
        amount=amount,
    )
    Transaction.objects.filter(pk=row.pk).update(created_at=created_at)
    return row


@pytest.fixture
def rows(account):
    now = timezone.now()
    _create_row(account, Transaction.INCOME, "80.00", now - timedelta(days=10))
    _create_row(account, Transaction.EXPENSE, "20.00", now - timedelta(days=5))
    _create_row(account, Transaction.INCOME, "15.00", now)
    return account


@pytest.mark.django_db
def test_summary_totals(auth_client, rows, account):
    response = auth_client.get(f"/api/accounts/{account.uuid}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["__balance__"] == "200.00"
    assert data["__income_total__"] == "95.00"
    assert data["__expense_total__"] == "20.00"
    assert data["__count__"] == 3


@pytest.mark.django_db
def test_summary_filters_by_type(auth_client, rows, account):
    response = auth_client.get(
        f"/api/accounts/{account.uuid}/summary",
        {"transaction_type": "expense"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["__income_total__"] == "0.00"
    assert data["__expense_total__"] == "20.00"
    assert data["__count__"] == 1


@pytest.mark.django_db
def test_list_filters_by_type(auth_client, rows, account):
    response = auth_client.get(
        f"/api/accounts/{account.uuid}/transactions/",
        {"transaction_type": "income"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["__transaction_type__"] == "income" for item in data)


@pytest.mark.django_db
def test_summary_filters_by_date(auth_client, rows, account):
    today = timezone.now().date().isoformat()
    response = auth_client.get(
        f"/api/accounts/{account.uuid}/summary",
        {"date_from": today},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["__income_total__"] == "15.00"
    assert data["__expense_total__"] == "0.00"
    assert data["__count__"] == 1


@pytest.mark.django_db
def test_invalid_filter_values(auth_client, account):
    bad_type = auth_client.get(
        f"/api/accounts/{account.uuid}/summary",
        {"transaction_type": "transfer"},
    )
    assert bad_type.status_code == 400
    assert bad_type.json()["__detail__"] == "__invalid_transaction_type__"

    bad_date = auth_client.get(
        f"/api/accounts/{account.uuid}/transactions/",
        {"date_from": "not-a-date"},
    )
    assert bad_date.status_code == 400
    assert bad_date.json()["__detail__"] == "__invalid_date__"


@pytest.mark.django_db
def test_summary_other_users_account(auth_client, other_user):
    other_account = Account.objects.create(
        user=other_user,
        account_number="5555555555",
        account_type="checking",
    )
    response = auth_client.get(f"/api/accounts/{other_account.uuid}/summary")
    assert response.status_code == 404
