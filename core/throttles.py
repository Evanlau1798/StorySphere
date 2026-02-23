# core/throttles.py
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Limit login attempts to prevent brute-force attacks."""
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """Limit registration attempts to prevent abuse."""
    scope = 'register'
