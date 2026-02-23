"""
Authentication & Session Management Tests
- Registration with password validation
- Login (JWT token obtain)
- Token refresh
- JWT token claims (no test_field leakage)
- Protected endpoint access control
"""
import json
import base64
import pytest
from rest_framework import status


API_PREFIX = '/api'


def decode_jwt_payload(token):
    """Decode JWT payload without external library (avoids system PyJWT conflict)."""
    payload_b64 = token.split('.')[1]
    # Add padding
    payload_b64 += '=' * (4 - len(payload_b64) % 4)
    payload_bytes = base64.urlsafe_b64decode(payload_b64)
    return json.loads(payload_bytes)


class TestRegistration:
    def test_register_success(self, api_client, db):
        resp = api_client.post(f'{API_PREFIX}/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass99!',
            'password2': 'StrongPass99!',
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_register_password_mismatch(self, api_client, db):
        resp = api_client.post(f'{API_PREFIX}/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass99!',
            'password2': 'DifferentPass99!',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password_rejected(self, api_client, db):
        """Django password validators should reject weak passwords."""
        resp = api_client.post(f'{API_PREFIX}/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123',
            'password2': '123',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_common_password_rejected(self, api_client, db):
        resp = api_client.post(f'{API_PREFIX}/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password2': 'password123',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_username(self, api_client, reader_user):
        resp = api_client.post(f'{API_PREFIX}/auth/register/', {
            'username': 'reader',  # already exists
            'email': 'other@example.com',
            'password': 'StrongPass99!',
            'password2': 'StrongPass99!',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    def test_login_success(self, api_client, reader_user):
        resp = api_client.post(f'{API_PREFIX}/auth/token/', {
            'username': 'reader',
            'password': 'TestPass123!',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data
        assert 'refresh' in resp.data

    def test_login_wrong_password(self, api_client, reader_user):
        resp = api_client.post(f'{API_PREFIX}/auth/token/', {
            'username': 'reader',
            'password': 'WrongPassword!',
        })
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client, db):
        resp = api_client.post(f'{API_PREFIX}/auth/token/', {
            'username': 'ghost',
            'password': 'Whatever123!',
        })
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestJWTTokenClaims:
    def test_token_contains_role_and_username(self, api_client, author_user):
        resp = api_client.post(f'{API_PREFIX}/auth/token/', {
            'username': 'author',
            'password': 'TestPass123!',
        })
        assert resp.status_code == status.HTTP_200_OK
        payload = decode_jwt_payload(resp.data['access'])
        assert payload['username'] == 'author'
        assert payload['role'] == 'AUTHOR'

    def test_token_no_test_field(self, api_client, reader_user):
        """Ensure the debug test_field has been removed from JWT."""
        resp = api_client.post(f'{API_PREFIX}/auth/token/', {
            'username': 'reader',
            'password': 'TestPass123!',
        })
        assert resp.status_code == status.HTTP_200_OK
        payload = decode_jwt_payload(resp.data['access'])
        assert 'test_field' not in payload


class TestTokenRefresh:
    def test_refresh_token_works(self, api_client, reader_user):
        login_resp = api_client.post(f'{API_PREFIX}/auth/token/', {
            'username': 'reader',
            'password': 'TestPass123!',
        })
        refresh_token = login_resp.data['refresh']

        resp = api_client.post(f'{API_PREFIX}/auth/token/refresh/', {
            'refresh': refresh_token,
        })
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data

    def test_refresh_with_invalid_token(self, api_client, db):
        resp = api_client.post(f'{API_PREFIX}/auth/token/refresh/', {
            'refresh': 'invalid-token-string',
        })
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestProtectedEndpoints:
    def test_profile_requires_auth(self, api_client, db):
        resp = api_client.get(f'{API_PREFIX}/profile/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_accessible_with_auth(self, api_client, reader_user):
        api_client.force_authenticate(user=reader_user)
        resp = api_client.get(f'{API_PREFIX}/profile/')
        assert resp.status_code == status.HTTP_200_OK

    def test_bookshelf_requires_auth(self, api_client, db):
        resp = api_client.get(f'{API_PREFIX}/reading-progress/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_image_upload_requires_auth(self, api_client, db):
        resp = api_client.post(f'{API_PREFIX}/images/upload/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
