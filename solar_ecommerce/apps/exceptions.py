"""
Custom DRF exception handler – prevents leaking internal errors
while keeping standard error format for known exceptions.
"""

import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('django.security')


def custom_exception_handler(exc, context):
    """
    Extend DRF's default exception handler:
    - Known exceptions (400, 401, 403, 404, etc.) → standard DRF format
    - Unhandled exceptions (500) → log + generic message (no traceback leak)
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Known DRF exceptions – return as-is (keep API contract)
        return response

    # Unhandled exception – log and return generic 500
    view = context.get('view', None)
    logger.error(
        'Unhandled exception in %s: %s',
        view.__class__.__name__ if view else 'unknown',
        str(exc),
        exc_info=True,
    )
    return Response(
        {'detail': 'An internal server error occurred.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
