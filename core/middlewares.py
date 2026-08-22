from rest_framework.authentication import TokenAuthentication


class TokenAuthSupportCookie(TokenAuthentication):
    """
    Handles token-based authentication, including support
    for token provided via cookies.

    This class extends TokenAuthentication to read the token cookie.
    If the cookie is present and no Authorization header is set, the
    cookie value is used. Otherwise the usual TokenAuthentication
    behavior is unchanged.
    """

    def authenticate(self, request):
        cookie_token = request.COOKIES.get("token")
        if cookie_token and "HTTP_AUTHORIZATION" not in request.META:
            return self.authenticate_credentials(cookie_token)
        return super().authenticate(request)
