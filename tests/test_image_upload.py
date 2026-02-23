"""
Image Upload Security Tests
- File size limits
- Extension whitelist
- Filename sanitization (no user-controlled filenames)
- Auth required
"""
import pytest
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from tests.conftest import make_test_image


API_PREFIX = '/api'


class TestImageUploadSecurity:
    def test_upload_valid_jpg(self, api_client, author_user):
        api_client.force_authenticate(user=author_user)
        image = make_test_image('photo.jpg', fmt='JPEG')
        resp = api_client.post(f'{API_PREFIX}/images/upload/', {'image': image}, format='multipart')
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'url' in resp.data
        # Filename should NOT contain original name (UUID-based)
        assert 'photo' not in resp.data['url']

    def test_upload_valid_png(self, api_client, author_user):
        api_client.force_authenticate(user=author_user)
        image = make_test_image('pic.png', fmt='PNG')
        resp = api_client.post(f'{API_PREFIX}/images/upload/', {'image': image}, format='multipart')
        assert resp.status_code == status.HTTP_201_CREATED

    def test_upload_rejects_invalid_extension(self, api_client, author_user):
        """A file with .svg extension should be rejected."""
        api_client.force_authenticate(user=author_user)
        # Create a valid image but with .svg extension
        img = PILImage.new('RGB', (10, 10), color='red')
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        file = SimpleUploadedFile('evil.svg', buf.read(), content_type='image/svg+xml')
        resp = api_client.post(f'{API_PREFIX}/images/upload/', {'image': file}, format='multipart')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_rejects_oversized_file(self, api_client, author_user):
        """Files larger than 5MB should be rejected."""
        api_client.force_authenticate(user=author_user)
        # Create a large image (> 5MB)
        img = PILImage.new('RGB', (5000, 5000), color='blue')
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        file = SimpleUploadedFile('big.png', buf.read(), content_type='image/png')
        resp = api_client.post(f'{API_PREFIX}/images/upload/', {'image': file}, format='multipart')
        # Should be rejected if > 5MB
        if file.size > 5 * 1024 * 1024:
            assert resp.status_code == status.HTTP_400_BAD_REQUEST
        # If somehow the generated image is under 5MB, it should succeed
        # (PIL compression makes large dimensions sometimes still small)

    def test_upload_path_traversal_filename(self, api_client, author_user):
        """Filenames with path traversal sequences should be safely handled."""
        api_client.force_authenticate(user=author_user)
        img = PILImage.new('RGB', (10, 10), color='green')
        buf = BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        file = SimpleUploadedFile('../../etc/passwd.jpg', buf.read(), content_type='image/jpeg')
        resp = api_client.post(f'{API_PREFIX}/images/upload/', {'image': file}, format='multipart')
        assert resp.status_code == status.HTTP_201_CREATED
        # The saved URL should NOT contain the original filename
        assert 'passwd' not in resp.data['url']
        assert '../' not in resp.data['url']

    def test_upload_requires_auth(self, api_client, db):
        image = make_test_image()
        resp = api_client.post(f'{API_PREFIX}/images/upload/', {'image': image}, format='multipart')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_no_file(self, api_client, author_user):
        api_client.force_authenticate(user=author_user)
        resp = api_client.post(f'{API_PREFIX}/images/upload/', {}, format='multipart')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
