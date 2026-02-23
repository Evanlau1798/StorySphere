import os
import re
from html import escape as html_escape
from django.http import HttpResponse
from django.conf import settings
from .models import Novel, AuthorProfile


def _sanitize_for_html(text):
    """Escape all HTML special characters to prevent XSS in injected SEO content."""
    return html_escape(str(text), quote=True)


def _strip_html_tags(text):
    """Remove HTML tags and then escape the remaining text."""
    clean = re.sub(r'<[^>]+>', '', text)
    return _sanitize_for_html(clean)


def _read_index_html():
    """Read the built frontend index.html, returning content or an error response."""
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read(), None
    except FileNotFoundError:
        return None, HttpResponse("Frontend not built.", status=500)


def _inject_seo(html_content, title, description, cover_url, og_type="website"):
    """Inject sanitized SEO meta tags into the HTML content."""
    meta_tags = f"""
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{cover_url}" />
    <meta property="og:type" content="{og_type}" />
    <meta name="description" content="{description}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{cover_url}" />
    """

    if '<title>' in html_content:
        html_content = html_content.replace(
            '<title>Vite + Vue + TS</title>',
            f'<title>{title}</title>'
        )
    else:
        meta_tags += f"<title>{title}</title>"

    if '</head>' in html_content:
        html_content = html_content.replace('</head>', f'{meta_tags}</head>')

    seo_body_content = f"""
    <div style="position: absolute; left: -9999px; top: -9999px;">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    """
    if '<body>' in html_content:
        html_content = html_content.replace('<body>', f'<body>{seo_body_content}')

    return html_content


def packet_novel_seo(request, pk):
    html_content, error_response = _read_index_html()
    if error_response:
        return error_response

    try:
        novel_obj = Novel.objects.get(pk=pk)
    except Novel.DoesNotExist:
        return HttpResponse(html_content)

    # Sanitize all user-controlled data before HTML injection
    title = _sanitize_for_html(f"{novel_obj.title} - {novel_obj.author.pen_name}")
    raw_desc = novel_obj.description[:150] + "..." if len(novel_obj.description) > 150 else novel_obj.description
    description = _sanitize_for_html(raw_desc.replace('\n', ' '))

    cover_url = ""
    if novel_obj.cover_image:
        cover_url = _sanitize_for_html(request.build_absolute_uri(novel_obj.cover_image.url))

    html_content = _inject_seo(html_content, title, description, cover_url, og_type="book")
    return HttpResponse(html_content)


def packet_sitemap(request):
    """Generates a simple sitemap.xml for novels."""
    novels = Novel.objects.all().order_by('-updated_at')
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    base_url = "https://novel.evanlau1798.com"

    # Static pages
    for path in ['', '/explore', '/leaderboard', '/updates']:
        xml_content.append('<url>')
        xml_content.append(f'<loc>{base_url}{path}</loc>')
        xml_content.append('<changefreq>daily</changefreq>')
        xml_content.append('</url>')

    # Dynamic Novel pages
    for novel in novels:
        xml_content.append('<url>')
        xml_content.append(f'<loc>{base_url}/novel/{novel.id}</loc>')
        xml_content.append(f'<lastmod>{novel.updated_at.strftime("%Y-%m-%d")}</lastmod>')
        xml_content.append('<changefreq>daily</changefreq>')
        xml_content.append('</url>')

    xml_content.append('</urlset>')
    return HttpResponse('\n'.join(xml_content), content_type="application/xml")


def packet_author_seo(request, pk):
    """Injects SEO tags for Author pages."""
    html_content, error_response = _read_index_html()
    if error_response:
        return error_response

    try:
        author = AuthorProfile.objects.get(user_id=pk)
    except AuthorProfile.DoesNotExist:
        return HttpResponse(html_content)

    # Sanitize all user-controlled data
    title = _sanitize_for_html(f"{author.pen_name} - 小說作者")
    # Strip HTML tags from bio, then escape the result
    clean_bio = re.sub(r'<[^>]+>', '', author.bio)
    raw_desc = clean_bio[:150] + "..." if len(clean_bio) > 150 else clean_bio
    description = _sanitize_for_html(raw_desc.replace('\n', ' '))

    cover_url = ""
    if author.user.avatar:
        cover_url = _sanitize_for_html(request.build_absolute_uri(author.user.avatar.url))

    html_content = _inject_seo(html_content, title, description, cover_url, og_type="profile")
    return HttpResponse(html_content)


def packet_general_seo(request):
    """Injects SEO tags for general pages (Home, Explore, etc)."""
    html_content, error_response = _read_index_html()
    if error_response:
        return error_response

    path = request.path

    meta_map = {
        '/': {
            'title': 'StorySphere - 探索無限的故事宇宙',
            'description': 'StorySphere 是一個專為小說愛好者打造的閱讀平台。在這裡，您可以發現各類原創小說，與作者互動，並建立屬於您的個人書架。'
        },
        '/explore': {
            'title': '探索小說 - StorySphere',
            'description': '瀏覽最新、最熱門的小說作品，發現您的下一個最愛。'
        },
        '/leaderboard': {
            'title': '排行榜 - StorySphere',
            'description': '查看本週人氣最高、觀看次數最多的小說排行榜。'
        },
        '/updates': {
            'title': '最近更新 - StorySphere',
            'description': '追蹤剛剛更新章節的小說，不錯過任何精彩內容。'
        }
    }

    # Normalize path (remove trailing slash for checking)
    check_path = path.rstrip('/') if path != '/' else '/'
    data = meta_map.get(check_path, meta_map['/'])

    # These are hardcoded values (not user input), but sanitize for consistency
    title = _sanitize_for_html(data['title'])
    description = _sanitize_for_html(data['description'])
    cover_url = "https://novel.evanlau1798.com/logo.png"

    html_content = _inject_seo(html_content, title, description, cover_url)
    return HttpResponse(html_content)
