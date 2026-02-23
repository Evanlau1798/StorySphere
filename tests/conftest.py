import pytest
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from core.models import CustomUser, AuthorProfile, Novel, Chapter, Volume


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def reader_user(db):
    user = CustomUser.objects.create_user(
        username='reader',
        email='reader@example.com',
        password='TestPass123!',
        role=CustomUser.Role.READER,
    )
    return user


@pytest.fixture
def author_user(db):
    user = CustomUser.objects.create_user(
        username='author',
        email='author@example.com',
        password='TestPass123!',
        role=CustomUser.Role.AUTHOR,
    )
    # Signal auto-creates AuthorProfile, but set pen_name
    user.author_profile.pen_name = '測試作者'
    user.author_profile.bio = '<p>作者簡介</p>'
    user.author_profile.save()
    return user


@pytest.fixture
def author_user_2(db):
    user = CustomUser.objects.create_user(
        username='author2',
        email='author2@example.com',
        password='TestPass123!',
        role=CustomUser.Role.AUTHOR,
    )
    user.author_profile.pen_name = '另一位作者'
    user.author_profile.save()
    return user


@pytest.fixture
def admin_user(db):
    user = CustomUser.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='TestPass123!',
        role=CustomUser.Role.ADMIN,
    )
    return user


@pytest.fixture
def novel(author_user):
    return Novel.objects.create(
        title='測試小說',
        author=author_user.author_profile,
        description='這是一本測試小說。',
        status=Novel.Status.ONGOING,
        category=Novel.Category.FANTASY,
    )


@pytest.fixture
def volume(novel):
    return Volume.objects.create(
        novel=novel,
        title='第一卷',
        order=1,
    )


@pytest.fixture
def chapter(novel):
    return Chapter.objects.create(
        novel=novel,
        title='第一章',
        content='<p>這是第一章的內容。</p>',
        order=1,
        status=Chapter.Status.PUBLISHED,
    )


@pytest.fixture
def draft_chapter(novel):
    return Chapter.objects.create(
        novel=novel,
        title='草稿章節',
        content='<p>這是草稿內容。</p>',
        order=2,
        status=Chapter.Status.DRAFT,
    )


@pytest.fixture
def novel_by_author2(author_user_2):
    return Novel.objects.create(
        title='另一本小說',
        author=author_user_2.author_profile,
        description='另一位作者的小說。',
        status=Novel.Status.ONGOING,
    )


def make_test_image(name='test.jpg', size=(100, 100), fmt='JPEG'):
    """Create a minimal valid image file for upload testing."""
    img = PILImage.new('RGB', size, color='red')
    buf = BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    ext_map = {'JPEG': '.jpg', 'PNG': '.png', 'GIF': '.gif'}
    return SimpleUploadedFile(name, buf.read(), content_type=f'image/{fmt.lower()}')
