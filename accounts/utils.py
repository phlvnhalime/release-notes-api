from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from accounts.models import UserABS


def get_user(email, password):
    user = UserABS.objects.filter(
        email=email,
        is_active=True,
        deleted_at__isnull=True,
    ).first()
    if user is None or not user.check_password(password):
        return None
    return user


def auth_response(user, status=200):
    Token.objects.filter(user=user).delete()
    token, _ = Token.objects.get_or_create(user=user)
    response = Response(user.to_dict(), status=status)
    response.set_cookie(
        settings.AUTH_COOKIE,
        token.key,
        httponly=True,
        samesite="Lax",
    )
    return response
