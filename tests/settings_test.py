"""
Test-specific Django settings.
Uses SQLite in-memory database for fast, isolated tests.
"""
import os
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-pytest-only')
os.environ.setdefault('DEBUG', 'True')
# Must set DB vars before importing settings to prevent errors
os.environ.setdefault('DB_NAME', 'test')
os.environ.setdefault('DB_USER', 'test')
os.environ.setdefault('DB_PASSWORD', 'test')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')

from novel_backend.settings import *  # noqa: F401, F403

# Override database to use SQLite in-memory for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable throttling in most tests (specific tests override this)
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []

# Use fast password hasher for test speed
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Simplified logging: remove discord handler to avoid import errors
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
