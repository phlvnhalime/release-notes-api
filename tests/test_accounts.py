import pytest

from accounts.models import Account, UserABS


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
    )


@pytest.mark.django_db
def test_list_accounts(auth_client, account):
    response = auth_client.get("/api/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["__account_number__"] == "9876543210"


@pytest.mark.django_db
def test_list_accounts_requires_auth(client):
    response = client.get("/api/accounts/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_account(auth_client):
    response = auth_client.post(
        "/api/accounts/",
        {"account_number": "1111111111", "account_type": "savings"},
        content_type="application/json",
    )
    assert response.status_code == 201
    assert response.json()["__account_number__"] == "1111111111"
    assert response.json()["__account_type__"] == "savings"
    assert response.json()["__balance__"] == "0"


@pytest.mark.django_db
def test_create_account_duplicate_number(auth_client, account):
    response = auth_client.post(
        "/api/accounts/",
        {"account_number": "9876543210", "account_type": "savings"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json()["__detail__"] == "__account_number_exists__"


@pytest.mark.django_db
def test_get_account(auth_client, account):
    response = auth_client.get(f"/api/accounts/{account.uuid}")
    assert response.status_code == 200
    assert response.json()["__account_number__"] == "9876543210"


@pytest.mark.django_db
def test_get_other_users_account(auth_client, other_user):
    other_account = Account.objects.create(
        user=other_user,
        account_number="5555555555",
        account_type="checking",
    )
    response = auth_client.get(f"/api/accounts/{other_account.uuid}")
    assert response.status_code == 404


@pytest.mark.django_db
def test_update_account(auth_client, account):
    response = auth_client.patch(
        f"/api/accounts/{account.uuid}",
        {"account_type": "savings"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["__account_type__"] == "savings"


@pytest.mark.django_db
def test_delete_account(auth_client, account):
    response = auth_client.delete(f"/api/accounts/{account.uuid}")
    assert response.status_code == 200
    assert response.json()["__detail__"] == "__deleted__"
    account.refresh_from_db()
    assert account.deleted_at is not None

    list_response = auth_client.get("/api/accounts/")
    assert list_response.json() == []
