# novel_backend/core/urls.py
from django.urls import path, include
from .views import (
    UserRegistrationView,
    UserProfileView,
    AuthorDetailView,
    ReadingProgressViewSet,
    NovelViewSet,
    ChapterViewSet,
    VolumeViewSet,
    ImageView,
    MyTokenObtainPairView, # Re-import our custom view
    novel_analytics,
    log_frontend_error, # Import the new view
)
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r'novels', NovelViewSet, basename='novel')
router.register(r'reading-progress', ReadingProgressViewSet, basename='reading-progress') # 註冊 ReadingProgressViewSet

novels_router = routers.NestedDefaultRouter(router, r'novels', lookup='novel')
novels_router.register(r'volumes', VolumeViewSet, basename='novel-volumes')
novels_router.register(r'chapters', ChapterViewSet, basename='novel-chapters')

volumes_router = routers.NestedDefaultRouter(novels_router, r'volumes', lookup='volume')
volumes_router.register(r'chapters', ChapterViewSet, basename='volume-chapters')

urlpatterns = [
    # 使用者認證
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), # Use our custom view
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 個人檔案
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # 作者公開頁
    path('authors/<int:user_id>/', AuthorDetailView.as_view(), name='author-detail'),

    # 圖片上傳
    path('images/upload/', ImageView.as_view(), name='image-upload'),

    # 前端錯誤日誌
    path('log-frontend-error/', log_frontend_error, name='log-frontend-error'),

    # 小說分析
    path('novels/<int:pk>/analytics/', novel_analytics, name='novel-analytics'),

    # 小說 (必須放在章節 URL 之後，以避免路由衝突)
    path('', include(router.urls)),
    path('', include(novels_router.urls)),
    path('', include(volumes_router.urls)),
]