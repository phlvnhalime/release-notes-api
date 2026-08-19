from rest_framework.authentication import TokenAuthentication

class TokenAuthSupportCookie(TokenAuthentication):
    """
    Handles token-based authentication, including support for token provided via cookies.

    this class extends the TokenAuthentication class to add support for token provided via cookies.
    Specifically, it checks for the presence of the 'token' cookie and if it exists, it uses that token to authenticate the request.
    If the 'token' cookie is not present, it falls back to the standard token authentication.TokenAuthentication behavior is unchanged otherwise.
    """
    def authenticate(self, request):
        if 'token' in request.COOKIES and "HTTP_AUTHORIZATION" not in request.META:
            return self.authenticate_credentials(request.COOKIES.get('token'))
        return super().authenticate(request)
