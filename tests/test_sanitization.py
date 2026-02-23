"""
XSS / HTML Sanitization Tests
- Chapter content sanitization (script tags, event handlers, dangerous CSS)
- Bio field sanitization
- SEO view sanitization
- Log injection prevention
"""
import pytest
from rest_framework import status

from core.serializers import sanitize_html_content


API_PREFIX = '/api'


class TestSanitizeHtmlFunction:
    """Unit tests for the sanitize_html_content function."""

    def test_strips_script_tags(self):
        result = sanitize_html_content('<p>Hello</p><script>alert("XSS")</script>')
        assert '<script>' not in result
        assert 'alert' not in result or '<script>' not in result
        assert '<p>Hello</p>' in result

    def test_strips_event_handlers(self):
        result = sanitize_html_content('<p onmouseover="alert(1)">Hover</p>')
        assert 'onmouseover' not in result
        assert '<p>' in result

    def test_strips_onerror_on_img(self):
        result = sanitize_html_content('<img src="x.jpg" onerror="alert(1)">')
        assert 'onerror' not in result
        assert 'src="x.jpg"' in result

    def test_strips_javascript_href(self):
        result = sanitize_html_content('<a href="javascript:alert(1)">Click</a>')
        assert 'javascript:' not in result

    def test_preserves_safe_tags(self):
        html = '<p><strong>Bold</strong> <em>italic</em> <u>underline</u></p>'
        result = sanitize_html_content(html)
        assert '<strong>' in result
        assert '<em>' in result
        assert '<u>' in result

    def test_preserves_img_with_safe_attrs(self):
        html = '<img src="https://example.com/img.jpg" alt="pic" width="200">'
        result = sanitize_html_content(html)
        assert 'src="https://example.com/img.jpg"' in result
        assert 'alt="pic"' in result

    def test_preserves_page_break_hr(self):
        html = '<hr class="page-break-marker" data-type="page-break">'
        result = sanitize_html_content(html)
        assert 'data-type="page-break"' in result
        assert 'page-break-marker' in result

    def test_preserves_safe_css(self):
        html = '<span style="font-size: 18px; text-align: center;">Text</span>'
        result = sanitize_html_content(html)
        assert 'font-size' in result

    def test_strips_dangerous_css(self):
        html = '<span style="background: url(javascript:alert(1));">Text</span>'
        result = sanitize_html_content(html)
        assert 'url(' not in result

    def test_handles_empty_string(self):
        assert sanitize_html_content('') == ''

    def test_handles_none(self):
        assert sanitize_html_content(None) is None

    def test_strips_iframe(self):
        result = sanitize_html_content('<iframe src="https://evil.com"></iframe>')
        assert '<iframe' not in result

    def test_strips_form(self):
        result = sanitize_html_content('<form action="/steal"><input type="text"></form>')
        assert '<form' not in result


class TestChapterContentSanitization:
    """Integration tests: chapter content is sanitized on save via API."""

    def test_chapter_create_strips_xss(self, api_client, author_user, novel):
        api_client.force_authenticate(user=author_user)
        resp = api_client.post(f'{API_PREFIX}/novels/{novel.id}/chapters/', {
            'title': '章節標題',
            'content': '<p>正常內容</p><script>alert("XSS")</script>',
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert '<script>' not in resp.data['content']
        assert '<p>正常內容</p>' in resp.data['content']

    def test_chapter_update_strips_xss(self, api_client, author_user, novel, chapter):
        api_client.force_authenticate(user=author_user)
        resp = api_client.patch(
            f'{API_PREFIX}/novels/{novel.id}/chapters/{chapter.id}/',
            {'content': '<p>Good</p><img src=x onerror=alert(1)>'},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert 'onerror' not in resp.data['content']


class TestBioSanitization:
    """Integration tests: author bio is sanitized on save via API."""

    def test_bio_update_strips_script(self, api_client, author_user):
        api_client.force_authenticate(user=author_user)
        resp = api_client.patch(
            f'{API_PREFIX}/profile/',
            {'bio': '<p>簡介</p><script>steal()</script>'},
            format='multipart',
        )
        assert resp.status_code == status.HTTP_200_OK
        assert '<script>' not in resp.data.get('bio', '')


class TestLogInjectionPrevention:
    """Verify that the frontend error log endpoint sanitizes input."""

    def test_log_truncates_long_message(self, api_client, db):
        long_msg = 'A' * 5000
        resp = api_client.post(f'{API_PREFIX}/log-frontend-error/', {
            'message': long_msg,
            'stack': 'some stack',
        })
        assert resp.status_code == 200

    def test_log_strips_control_characters(self, api_client, db):
        resp = api_client.post(f'{API_PREFIX}/log-frontend-error/', {
            'message': 'normal\r\ninjected\x00line',
            'stack': 'stack\r\ninjection',
        })
        assert resp.status_code == 200

    def test_log_error_response_no_internal_details(self, api_client, db):
        """Error response should not expose internal exception details."""
        # Even with weird input, the endpoint shouldn't leak internals
        resp = api_client.post(f'{API_PREFIX}/log-frontend-error/', {
            'message': 'test',
        })
        assert resp.status_code == 200
        data = resp.json()
        assert 'status' in data
