import os
from django.http import HttpResponse, Http404
from django.conf import settings
from .models import Novel

def packet_novel_seo(request, pk):
    try:
        novel = Novel.objects.get(pk=pk)
    except Novel.DoesNotExist:
        # Fallback to standard index.html if novel not found, or 404.
        # Ideally, just serve index.html and let Vue handle 404, but we want SEO.
        # Let's serve index.html untouched so Vue shows 404 page.
        pass

    # Path to the built frontend index.html
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        return HttpResponse("Frontend not built.", status=500)

    # Note: 'novel' variable might be undefined if DoesNotExist happened and we "pass".
    # Rethink logic:
    novel_obj = None
    try:
        novel_obj = Novel.objects.get(pk=pk)
    except Novel.DoesNotExist:
        return HttpResponse(html_content) # Return standard HTML, Vue handles 404

    # Prepare logic for injection
    title = f"{novel_obj.title} - {novel_obj.author.pen_name}"
    description = novel_obj.description[:150] + "..." if len(novel_obj.description) > 150 else novel_obj.description
    # Escape quotes to prevent breaking HTML
    title = title.replace('"', '&quot;')
    description = description.replace('"', '&quot;').replace('\n', ' ')
    
    cover_url = ""
    if novel_obj.cover_image:
        # Assuming MEDIA_URL is /media/
        cover_url = request.build_absolute_uri(novel_obj.cover_image.url)

    # Meta tags to inject
    # We will replace <title>...</title> and add other tags before </head>
    
    meta_tags = f"""
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{cover_url}" />
    <meta property="og:type" content="book" />
    <meta name="description" content="{description}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{cover_url}" />
    """

    # Simple string replacement. 
    # NOTE: index.html has <title>Vite + Vue + TS</title>
    
    if '<title>' in html_content:
        html_content = html_content.replace(
            f'<title>Vite + Vue + TS</title>', 
            f'<title>{title}</title>'
        )
    else:
         meta_tags += f"<title>{title}</title>"

    if '</head>' in html_content:
        html_content = html_content.replace('</head>', f'{meta_tags}</head>')
    
    # Inject SEO content (H1, Description) into body for crawlers
    # Using a hidden div or noscript is one way, but Google renders JS. 
    # However, to satisfy "H1 missing" tools, we put it in the raw HTML.
    # We place it before #app so it's present in the DOM. 
    seo_body_content = f"""
    <div style="position: absolute; left: -9999px; top: -9999px;">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    """
    if '<body>' in html_content:
        html_content = html_content.replace('<body>', f'<body>{seo_body_content}')

    return HttpResponse(html_content)

def packet_sitemap(request):
    """Generates a simple sitemap.xml for novels."""
    novels = Novel.objects.all().order_by('-updated_at')
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Base URL - assuming https://novel.evanlau1798.com
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

from .models import AuthorProfile

def packet_author_seo(request, pk):
    """Injects SEO tags for Author pages."""
    try:
        # Assuming user_id is the pk for author url /author/<id> based on urls
        author = AuthorProfile.objects.get(user_id=pk)
    except AuthorProfile.DoesNotExist:
        # Fallback to standard index
        index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            return HttpResponse("Frontend not built.", status=500)

    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        return HttpResponse("Frontend not built.", status=500)

    title = f"{author.pen_name} - 小說作者"
    # Create a cleaner textual bio
    import re
    clean_bio = re.sub('<[^<]+?>', '', author.bio) # Remove HTML tags
    description = clean_bio[:150] + "..." if len(clean_bio) > 150 else clean_bio
    description = description.replace('"', '&quot;').replace('\n', ' ')
    
    cover_url = ""
    if author.user.avatar:
        cover_url = request.build_absolute_uri(author.user.avatar.url)

    meta_tags = f"""
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{cover_url}" />
    <meta property="og:type" content="profile" />
    <meta name="description" content="{description}" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{cover_url}" />
    """

    if '<title>' in html_content:
        html_content = html_content.replace(f'<title>Vite + Vue + TS</title>', f'<title>{title}</title>')
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

    return HttpResponse(html_content)

def packet_general_seo(request):
    """Injects SEO tags for general pages (Home, Explore, etc)."""
    path = request.path
    
    meta_map = {
        '/': {
            'title': 'StroySphere - 您的線上小說閱讀平台',
            'description': '提供各類原創小說、輕小說在線閱讀。奇幻、科幻、言情、都市應有盡有。'
        },
        '/explore': {
            'title': '探索小說 - StroySphere',
            'description': '瀏覽最新、最熱門的小說作品，發現您的下一個最愛。'
        },
        '/leaderboard': {
            'title': '排行榜 - StroySphere',
            'description': '查看本週人氣最高、觀看次數最多的小說排行榜。'
        },
        '/updates': {
            'title': '最近更新 - StroySphere',
            'description': '追蹤剛剛更新章節的小說，不錯過任何精彩內容。'
        }
    }
    
    # Normalize path (remove trailing slash for checking)
    check_path = path.rstrip('/') if path != '/' else '/'
    data = meta_map.get(check_path, meta_map['/'])

    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        return HttpResponse("Frontend not built.", status=500)

    title = data['title']
    description = data['description']
    
    # Use logo or default image
    cover_url = "https://novel.evanlau1798.com/logo.png" # Assuming a logo exists, or use empty
    
    meta_tags = f"""
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{cover_url}" />
    <meta property="og:type" content="website" />
    <meta name="description" content="{description}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{cover_url}" />
    """

    if '<title>' in html_content:
         html_content = html_content.replace(f'<title>Vite + Vue + TS</title>', f'<title>{title}</title>')
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

    return HttpResponse(html_content)
