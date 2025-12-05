from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from core.seo_views import packet_novel_seo, packet_sitemap, packet_author_seo, packet_general_seo

def metrics_view(request):
    """A simple view to handle /metrics requests from monitoring systems."""
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    # 將所有 /api/ 開頭的請求都轉發到 core.urls
    path('api/', include('core.urls')), 
    # SEO Injection for Novel Details
    path('novel/<int:pk>/', packet_novel_seo),
    path('novel/<int:pk>', packet_novel_seo), 
    
    # SEO Injection for Author Details
    path('author/<int:pk>/', packet_author_seo),
    path('author/<int:pk>', packet_author_seo),

    # SEO for General Pages
    path('explore', packet_general_seo),
    path('explore/', packet_general_seo),
    path('leaderboard', packet_general_seo),
    path('leaderboard/', packet_general_seo),
    path('updates', packet_general_seo),
    path('updates/', packet_general_seo),
    path('', packet_general_seo), # Home page

    path('sitemap.xml', packet_sitemap), 
    # Handle /metrics requests to avoid 404 errors in logs
    path('metrics', metrics_view, name='metrics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)