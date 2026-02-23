"""
Model & Serializer Validation Tests
- User roles and author profile auto-creation
- Novel/Chapter/Volume model integrity
- Reading progress behavior
- Chapter draft vs published visibility
"""
import pytest
from rest_framework import status

from core.models import CustomUser, AuthorProfile, Novel, Chapter, Volume, ReadingProgress


API_PREFIX = '/api'


class TestUserModel:
    def test_default_role_is_reader(self, db):
        user = CustomUser.objects.create_user(
            username='defaultrole', email='dr@example.com', password='Pass123!'
        )
        assert user.role == CustomUser.Role.READER

    def test_author_profile_auto_created(self, db):
        user = CustomUser.objects.create_user(
            username='newauthor', email='na@example.com',
            password='Pass123!', role=CustomUser.Role.AUTHOR,
        )
        assert hasattr(user, 'author_profile')
        assert AuthorProfile.objects.filter(user=user).exists()

    def test_reader_has_no_author_profile(self, db):
        user = CustomUser.objects.create_user(
            username='purereader', email='pr@example.com', password='Pass123!',
        )
        assert not AuthorProfile.objects.filter(user=user).exists()


class TestNovelModel:
    def test_novel_str(self, novel):
        assert str(novel) == '測試小說'

    def test_novel_default_status(self, author_user):
        novel = Novel.objects.create(
            title='New', author=author_user.author_profile, description='desc',
        )
        assert novel.status == Novel.Status.ONGOING

    def test_novel_default_category(self, author_user):
        novel = Novel.objects.create(
            title='New', author=author_user.author_profile, description='desc',
        )
        assert novel.category == Novel.Category.OTHERS


class TestChapterModel:
    def test_chapter_default_status_is_draft(self, novel):
        chapter = Chapter.objects.create(
            novel=novel, title='Ch', content='text', order=99,
        )
        assert chapter.status == Chapter.Status.DRAFT

    def test_chapter_unique_order_per_novel(self, novel, chapter):
        """Two chapters in the same novel cannot have the same order."""
        with pytest.raises(Exception):
            Chapter.objects.create(
                novel=novel, title='Dup', content='text', order=chapter.order,
            )


class TestChapterVisibility:
    """Verify that draft chapters are not visible to public readers."""

    def test_public_novel_detail_hides_drafts(self, api_client, novel, chapter, draft_chapter):
        resp = api_client.get(f'{API_PREFIX}/novels/{novel.id}/')
        assert resp.status_code == status.HTTP_200_OK
        # The chapters_without_volume should only contain published chapters
        chapters = resp.data.get('chapters_without_volume', [])
        chapter_ids = [c['id'] for c in chapters]
        assert chapter.id in chapter_ids
        assert draft_chapter.id not in chapter_ids


class TestVolumeModel:
    def test_volume_order_auto_increment_via_api(self, api_client, author_user, novel):
        api_client.force_authenticate(user=author_user)
        resp1 = api_client.post(f'{API_PREFIX}/novels/{novel.id}/volumes/', {'title': '卷一'})
        resp2 = api_client.post(f'{API_PREFIX}/novels/{novel.id}/volumes/', {'title': '卷二'})
        assert resp1.status_code == status.HTTP_201_CREATED
        assert resp2.status_code == status.HTTP_201_CREATED
        assert resp2.data['order'] == resp1.data['order'] + 1


class TestReadingProgress:
    def test_add_to_bookshelf(self, api_client, reader_user, novel):
        api_client.force_authenticate(user=reader_user)
        resp = api_client.post(f'{API_PREFIX}/reading-progress/', {'novel': novel.id})
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    def test_bookshelf_isolated_per_user(self, api_client, reader_user, author_user, novel):
        """Each user should only see their own bookshelf."""
        # Reader adds to bookshelf
        api_client.force_authenticate(user=reader_user)
        api_client.post(f'{API_PREFIX}/reading-progress/', {'novel': novel.id})

        # Author should see empty bookshelf
        api_client.force_authenticate(user=author_user)
        resp = api_client.get(f'{API_PREFIX}/reading-progress/')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 0


class TestViewCounter:
    def test_novel_view_increments(self, api_client, novel):
        original_views = novel.views
        api_client.get(f'{API_PREFIX}/novels/{novel.id}/')
        novel.refresh_from_db()
        assert novel.views == original_views + 1

    def test_chapter_view_increments(self, api_client, novel, chapter):
        original_views = chapter.views
        api_client.get(f'{API_PREFIX}/novels/{novel.id}/chapters/{chapter.id}/')
        chapter.refresh_from_db()
        assert chapter.views == original_views + 1
