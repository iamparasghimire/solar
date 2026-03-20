"""
Security middleware – adds defense-in-depth headers
and strips null bytes from input to prevent injection attacks.
"""

import re
from django.http import HttpResponseBadRequest


class SecurityHeadersMiddleware:
    """Add extra security headers that Django doesn't set by default."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Permissions-Policy: disable unused browser features
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), payment=(self)'
        )
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        # Cache-control for API responses
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'
        return response


class InputSanitizationMiddleware:
    """
    Reject requests containing null bytes (common in injection attacks).
    Also reject excessively long query strings.
    """

    MAX_QUERY_STRING_LENGTH = 2048

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Block null bytes in path, query string, and body
        if '\x00' in request.path or '\x00' in request.META.get('QUERY_STRING', ''):
            return HttpResponseBadRequest('Invalid request.')

        # Block excessively long query strings (potential DoS)
        qs = request.META.get('QUERY_STRING', '')
        if len(qs) > self.MAX_QUERY_STRING_LENGTH:
            return HttpResponseBadRequest('Query string too long.')

        return self.get_response(request)
