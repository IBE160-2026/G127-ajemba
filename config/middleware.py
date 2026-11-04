"""Web safety headers for every response (AD-19)."""

CONTENT_SECURITY_POLICY = "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'"


class WebSafetyMiddleware:
    """Adds the content security policy, and no-store when a user is logged in.

    no-store stops the browser from keeping a logged-in page, so the Back button after
    logout does not show someone's lecture.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            response["Cache-Control"] = "no-store"
        return response
