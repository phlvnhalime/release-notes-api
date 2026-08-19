from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserABS
from accounts.utils import auth_response
from accounts.utils import get_user


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if not all([email, password, first_name, last_name]):
            return Response({"__detail__": "__fields_required__"}, status=400)

        if UserABS.objects.filter(email=email, deleted_at__isnull=True).exists():
            return Response({"__detail__": "__email_already_exists__"}, status=400)

        try:
            user = UserABS(
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.set_password(password)
            user.save()
            return auth_response(user, status=201)
        except Exception as e:
            return Response(
                {"__detail__": f"__error_creating_user__: {e}"},
                status=500,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"__detail__": "__email_and_password_required__"},
                status=400,
            )

        try:
            user = get_user(email, password)
            if user is None:
                return Response({"__detail__": "__invalid_credentials__"}, status=401)
            return auth_response(user)
        except Exception as e:
            return Response(
                {"__detail__": f"__error_logging_in__: {e}"},
                status=500,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        response = Response({"__detail__": "__logged_out__"})
        response.delete_cookie(settings.AUTH_COOKIE, samesite="Lax")
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(request.user.to_dict())
