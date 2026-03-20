"""
Shared pytest configuration & fixtures.
"""
import pytest


# Disable rate limiting in tests by setting very high throttle rates
@pytest.fixture(autouse=True)
def disable_throttling(settings):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        'DEFAULT_THROTTLE_RATES': {
            'anon': '10000/minute',
            'user': '10000/minute',
            'auth': '10000/minute',
            'contact': '10000/minute',
        },
    }
