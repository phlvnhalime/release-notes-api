from django.urls import path

from accounts.account_views import AccountDetailView, AccountListCreateView
from accounts.views import LoginView, LogoutView, MeView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"),
    path(
        "accounts/<int:account_id>/",
        AccountDetailView.as_view(),
        name="account-detail",
    ),
]
