from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def metrics_view(request):
    """A simple view to handle /metrics requests from monitoring systems."""
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    # 將所有 /api/ 開頭的請求都轉發到 core.urls
    path('api/', include('core.urls')), 
    # Handle /metrics requests to avoid 404 errors in logs
    path('metrics', metrics_view, name='metrics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)