"""
Rate Limiting Tests
- Verify throttle classes are configured on views
- Verify throttle rates are defined in settings
- Integration test with direct throttle instance
"""
import pytest
from rest_framework import status
from django.conf import settings


class TestThrottleConfiguration:
    """Verify that rate limiting is properly configured."""

    def test_login_view_has_login_throttle(self):
        from core.views import MyTokenObtainPairView
        from core.throttles import LoginRateThrottle
        assert LoginRateThrottle in MyTokenObtainPairView.throttle_classes

    def test_register_view_has_register_throttle(self):
        from core.views import UserRegistrationView
        from core.throttles import RegisterRateThrottle
        assert RegisterRateThrottle in UserRegistrationView.throttle_classes

    def test_login_throttle_scope_is_configured(self):
        from core.throttles import LoginRateThrottle
        throttle = LoginRateThrottle()
        assert throttle.scope == 'login'
        assert 'login' in settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})

    def test_register_throttle_scope_is_configured(self):
        from core.throttles import RegisterRateThrottle
        throttle = RegisterRateThrottle()
        assert throttle.scope == 'register'
        assert 'register' in settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})

    def test_global_throttle_rates_defined(self):
        rates = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})
        assert 'login' in rates
        assert 'register' in rates

    def test_login_rate_is_reasonable(self):
        """Login rate should be restrictive enough to prevent brute-force."""
        rates = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})
        rate = rates.get('login', '')
        # Parse "10/minute" -> (10, 'minute')
        num, period = rate.split('/')
        num = int(num)
        assert num <= 20, "Login rate should be restrictive"
        assert period in ('minute', 'min'), "Login rate should be per-minute"

    def test_register_rate_is_reasonable(self):
        """Registration rate should be restrictive enough to prevent abuse."""
        rates = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})
        rate = rates.get('register', '')
        num, period = rate.split('/')
        num = int(num)
        assert num <= 10, "Register rate should be restrictive"
