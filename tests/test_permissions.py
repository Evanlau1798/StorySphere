"""
Permission & Authorization Tests
- Ownership checks on Volume/Chapter create
- Author vs Reader vs Admin role access
- Cross-author write protection
- Admin endpoint access control
"""
import pytest
from rest_framework import status


API_PREFIX = '/api'


class TestNovelPermissions:
    def test_reader_cannot_create_novel(self, api_client, reader_user):
        api_client.force_authenticate(user=reader_user)
        resp = api_client.post(f'{API_PREFIX}/novels/', {
            'title': '讀者的小說',
            'description': '不應該成功',
        })
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_author_can_create_novel(self, api_client, author_user):
        api_client.force_authenticate(user=author_user)
        resp = api_client.post(f'{API_PREFIX}/novels/', {
            'title': '作者的新小說',
            'description': '應該成功',
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_anonymous_can_list_novels(self, api_client, novel):
        resp = api_client.get(f'{API_PREFIX}/novels/')
        assert resp.status_code == status.HTTP_200_OK

    def test_anonymous_can_retrieve_novel(self, api_client, novel):
        resp = api_client.get(f'{API_PREFIX}/novels/{novel.id}/')
        assert resp.status_code == status.HTTP_200_OK


class TestChapterOwnershipOnCreate:
    """Verify that only the novel's author can create chapters."""

    def test_author_can_create_chapter_in_own_novel(self, api_client, author_user, novel):
        api_client.force_authenticate(user=author_user)
        resp = api_client.post(f'{API_PREFIX}/novels/{novel.id}/chapters/', {
            'title': '新章節',
            'content': '<p>內容</p>',
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_other_author_cannot_create_chapter(self, api_client, author_user_2, novel):
        """Author 2 should NOT be able to create a chapter in Author 1's novel."""
        api_client.force_authenticate(user=author_user_2)
        resp = api_client.post(f'{API_PREFIX}/novels/{novel.id}/chapters/', {
            'title': '惡意章節',
            'content': '<p>不應該成功</p>',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_reader_cannot_create_chapter(self, api_client, reader_user, novel):
        api_client.force_authenticate(user=reader_user)
        resp = api_client.post(f'{API_PREFIX}/novels/{novel.id}/chapters/', {
            'title': '讀者章節',
            'content': '<p>不應該成功</p>',
        })
        # IsAuthorOrReadOnly has_permission allows safe methods only;
        # for unsafe methods, the user needs to be authenticated + AUTHOR role
        assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST)


class TestVolumeOwnershipOnCreate:
    """Verify that only the novel's author can create volumes."""

    def test_author_can_create_volume_in_own_novel(self, api_client, author_user, novel):
        api_client.force_authenticate(user=author_user)
        resp = api_client.post(f'{API_PREFIX}/novels/{novel.id}/volumes/', {
            'title': '新分卷',
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_other_author_cannot_create_volume(self, api_client, author_user_2, novel):
        """Author 2 should NOT be able to create a volume in Author 1's novel."""
        api_client.force_authenticate(user=author_user_2)
        resp = api_client.post(f'{API_PREFIX}/novels/{novel.id}/volumes/', {
            'title': '惡意分卷',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestChapterObjectPermissions:
    def test_author_can_update_own_chapter(self, api_client, author_user, novel, chapter):
        api_client.force_authenticate(user=author_user)
        resp = api_client.patch(
            f'{API_PREFIX}/novels/{novel.id}/chapters/{chapter.id}/',
            {'title': '更新標題'},
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_other_author_cannot_update_chapter(self, api_client, author_user_2, novel, chapter):
        api_client.force_authenticate(user=author_user_2)
        resp = api_client.patch(
            f'{API_PREFIX}/novels/{novel.id}/chapters/{chapter.id}/',
            {'title': '惡意更新'},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestAnalyticsPermissions:
    def test_author_can_view_own_analytics(self, api_client, author_user, novel):
        api_client.force_authenticate(user=author_user)
        resp = api_client.get(f'{API_PREFIX}/novels/{novel.id}/analytics/')
        assert resp.status_code == status.HTTP_200_OK

    def test_other_author_cannot_view_analytics(self, api_client, author_user_2, novel):
        api_client.force_authenticate(user=author_user_2)
        resp = api_client.get(f'{API_PREFIX}/novels/{novel.id}/analytics/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_view_analytics(self, api_client, novel):
        resp = api_client.get(f'{API_PREFIX}/novels/{novel.id}/analytics/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestAdminPermissions:
    def test_admin_can_access_stats(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.get(f'{API_PREFIX}/admin/stats/')
        assert resp.status_code == status.HTTP_200_OK

    def test_reader_cannot_access_admin(self, api_client, reader_user):
        api_client.force_authenticate(user=reader_user)
        resp = api_client.get(f'{API_PREFIX}/admin/stats/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_author_cannot_access_admin(self, api_client, author_user):
        api_client.force_authenticate(user=author_user)
        resp = api_client.get(f'{API_PREFIX}/admin/stats/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_access_admin(self, api_client, db):
        resp = api_client.get(f'{API_PREFIX}/admin/stats/')
        assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_modify_super_admin(self, api_client, admin_user, db):
        """User ID 1 (super admin) role cannot be changed."""
        # Create a user with id=1 if not exists
        from core.models import CustomUser
        super_admin, _ = CustomUser.objects.get_or_create(
            id=1,
            defaults={
                'username': 'superadmin',
                'email': 'super@example.com',
                'password': 'test',
                'role': CustomUser.Role.ADMIN,
            }
        )
        api_client.force_authenticate(user=admin_user)
        resp = api_client.patch(f'{API_PREFIX}/admin/1/update_role/', {
            'role': 'READER',
        })
        assert resp.status_code == status.HTTP_403_FORBIDDEN
