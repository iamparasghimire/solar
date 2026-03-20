"""
Custom throttle classes for sensitive endpoints.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Strict rate limit for login / register endpoints to prevent brute force."""
    scope = 'auth'


class ContactRateThrottle(AnonRateThrottle):
    """Rate limit for contact form / newsletter to prevent spam."""
    scope = 'contact'
