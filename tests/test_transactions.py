import pytest

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
        balance="100.00",
    )


@pytest.mark.django_db
def test_list_transactions_empty(auth_client, account):
    response = auth_client.get(f"/api/accounts/{account.id}/transactions/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_create_income_updates_balance(auth_client, account):
    response = auth_client.post(
        f"/api/accounts/{account.id}/transactions/",
        {
            "transaction_type": "income",
            "amount": "25.50",
            "description": "salary",
        },
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.json()
    assert data["__transaction_type__"] == "income"
    assert data["__amount__"] == "25.50"
    assert data["__description__"] == "salary"

    account.refresh_from_db()
    assert str(account.balance) == "125.50"


@pytest.mark.django_db
def test_create_expense_updates_balance(auth_client, account):
    response = auth_client.post(
        f"/api/accounts/{account.id}/transactions/",
        {"transaction_type": "expense", "amount": "40.00"},
        content_type="application/json",
    )
    assert response.status_code == 201
    account.refresh_from_db()
    assert str(account.balance) == "60.00"


@pytest.mark.django_db
def test_expense_rejects_insufficient_balance(auth_client, account):
    response = auth_client.post(
        f"/api/accounts/{account.id}/transactions/",
        {"transaction_type": "expense", "amount": "100.01"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json()["__detail__"] == "__insufficient_balance__"
    account.refresh_from_db()
    assert str(account.balance) == "100.00"


@pytest.mark.django_db
def test_create_transaction_requires_valid_fields(auth_client, account):
    response = auth_client.post(
        f"/api/accounts/{account.id}/transactions/",
        {"transaction_type": "transfer", "amount": "10"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json()["__detail__"] == "__fields_required__"


@pytest.mark.django_db
def test_cannot_transact_on_other_users_account(
    auth_client,
    other_user,
):
    other_account = Account.objects.create(
        user=other_user,
        account_number="5555555555",
        account_type="checking",
        balance="50.00",
    )
    response = auth_client.post(
        f"/api/accounts/{other_account.id}/transactions/",
        {"transaction_type": "income", "amount": "10"},
        content_type="application/json",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_transaction(auth_client, account):
    row = Transaction.objects.create(
        account=account,
        transaction_type=Transaction.INCOME,
        amount="10.00",
        description="gift",
    )
    response = auth_client.get(
        f"/api/accounts/{account.id}/transactions/{row.id}/",
    )
    assert response.status_code == 200
    assert response.json()["__description__"] == "gift"


@pytest.mark.django_db
def test_delete_expense_restores_balance(auth_client, account):
    create = auth_client.post(
        f"/api/accounts/{account.id}/transactions/",
        {"transaction_type": "expense", "amount": "30.00"},
        content_type="application/json",
    )
    transaction_id = create.json()["__id__"]

    response = auth_client.delete(
        f"/api/accounts/{account.id}/transactions/{transaction_id}/",
    )
    assert response.status_code == 200
    assert response.json()["__detail__"] == "__deleted__"

    account.refresh_from_db()
    assert str(account.balance) == "100.00"

    listed = auth_client.get(f"/api/accounts/{account.id}/transactions/")
    assert listed.json() == []
