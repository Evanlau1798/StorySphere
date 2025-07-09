# novel_backend/core/views.py

# --- Django & DRF Imports ---
from rest_framework import generics, viewsets, status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, Count, Prefetch
from django.db import models
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView as OriginalTokenObtainPairView
from django.http import JsonResponse
import logging

# --- Local Imports ---
from .models import CustomUser, AuthorProfile, Novel, Chapter, ReadingProgress, Volume # 引入 ReadingProgress 和 Volume
from .permissions import IsAuthorUserForWrite, IsAuthorOrReadOnly
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,     # 用於個人設定頁
    AuthorDetailSerializer,    # 用於作者公開頁
    NovelListSerializer,
    NovelDetailSerializer,
    ChapterSerializer,          # 用於章節列表
    ChapterDetailSerializer,    # 用於章節詳情
    ChapterEditSerializer,      # 用於章節編輯
    ReadingProgressSerializer,   # 用於書架與閱讀進度
    ImageUploadSerializer,
    CustomTokenObtainPairSerializer, # 引入新的 Serializer
    VolumeSerializer # 引入 VolumeSerializer
)

from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def log_frontend_error(request):
    try:
        error_data = request.data
        message = error_data.get('message', 'No message provided')
        stack = error_data.get('stack', 'No stack trace provided')
        
        # 使用 logger.error 來觸發 Discord 通知
        logger.error(f"Frontend Error: {message}\nStack Trace:\n{stack}")
        
        return JsonResponse({'status': 'ok'}, status=200)
    except Exception as e:
        # 如果日誌端點本身出錯，記錄到伺服器日誌
        logger.error(f"Error in log_frontend_error endpoint: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class MyTokenObtainPairView(OriginalTokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ImageView(generics.CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ImageUploadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data['image']
        # You might want to create a more sophisticated path, 
        # e.g., based on user or date
        path = f'chapter_images/{image.name}'
        saved_path = default_storage.save(path, image)
        url = default_storage.url(saved_path)
        return Response({'url': url}, status=status.HTTP_201_CREATED)



# ===================================================================
#  使用者 (User) & 個人檔案 (Profile) Views
# ===================================================================

class UserRegistrationView(generics.CreateAPIView):
    """
    允許任何人註冊新帳號。
    - POST /api/auth/register/
    """
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    獲取和更新當前登入使用者的個人資料。
    - GET /api/profile/ : 獲取自己的資料
    - PUT /api/profile/ : 更新自己的資料 (完整更新)
    - PATCH /api/profile/ : 更新自己的資料 (部分更新)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser]  # 支援檔案上傳 (頭像)

    def get_object(self):
        """永遠只返回當前登入的使用者物件。"""
        return self.request.user


# ===================================================================
#  作者 (Author) & 小說 (Novel) Views
# ===================================================================

class AuthorDetailView(generics.RetrieveAPIView):
    """
    獲取特定作者的公開資訊及其發表的小說列表。
    - GET /api/authors/{user_id}/
    """
    queryset = AuthorProfile.objects.all()
    serializer_class = AuthorDetailSerializer # 使用正確的 Serializer 名稱
    permission_classes = [AllowAny]
    lookup_field = 'user_id' # 使用 CustomUser 的 ID 來查詢


class ChapterDetailView(generics.RetrieveAPIView):
    """
    獲取單一章節的詳細內容，供閱讀頁使用。
    - GET /api/novels/{novel_pk}/chapters/{pk}/
    """
    queryset = Chapter.objects.all()
    serializer_class = ChapterDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """確保章節是從正確的小說中獲取的。"""
        return Chapter.objects.filter(novel_id=self.kwargs['novel_pk'])

class VolumeViewSet(viewsets.ModelViewSet):
    """
    處理所有與分卷相關的操作。
    """
    queryset = Volume.objects.all()
    serializer_class = VolumeSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        """確保分卷是從正確的小說中獲取的。"""
        novel_pk = self.kwargs.get('novel_pk')
        if novel_pk is None:
            return self.queryset.none() # 如果沒有 novel_pk，則不返回任何分卷
        return self.queryset.filter(novel_id=novel_pk).order_by('order')

    def perform_create(self, serializer):
        novel = Novel.objects.get(pk=self.kwargs['novel_pk'])
        # 自動計算 order
        last_volume = Volume.objects.filter(novel=novel).order_by('-order').first()
        next_order = (last_volume.order + 1) if last_volume else 1
        serializer.save(novel=novel, order=next_order)


class NovelViewSet(viewsets.ModelViewSet):
    """
    處理所有與小說相關的操作。
    """
    queryset = Novel.objects.all().order_by('-updated_at')

    def get_queryset(self):
        queryset = super().get_queryset()

        # If 'my_novels' query parameter is true and user is authenticated, filter by author
        if self.request.query_params.get('my_novels') == 'true' and self.request.user.is_authenticated:
            if hasattr(self.request.user, 'author_profile'):
                queryset = queryset.filter(author=self.request.user.author_profile)
            else:
                # If user is authenticated but not an author, return empty queryset for 'my_novels'
                return Novel.objects.none()

        # Correctly pre-load related data.
        # By using Prefetch without a custom queryset, Django will correctly
        # filter the related objects based on the parent novel.
        # We can still specify the ordering within the Prefetch object.
        return queryset.prefetch_related(
            Prefetch(
                'volumes',
                queryset=Volume.objects.order_by('order'),
                to_attr='volumes_ordered'  # Use a different attribute to avoid conflicts
            ),
            Prefetch(
                'chapters',
                queryset=Chapter.objects.filter(volume__isnull=True).order_by('order'),
                to_attr='chapters_without_volume'
            )
        ).annotate(
            # The calculation of total views still only calculates published ones
            total_views=Sum('chapters__views', filter=models.Q(chapters__status=Chapter.Status.PUBLISHED), default=0)
        )

    def get_serializer_context(self):
        """Passes context to the serializer to determine if it's an author's view."""
        context = super().get_serializer_context()
        user = self.request.user
        is_author_view = False

        if user.is_authenticated and hasattr(user, 'author_profile'):
            # Case 1: Author is viewing their own list of novels
            if self.action == 'list' and self.request.query_params.get('my_novels') == 'true':
                is_author_view = True
            # Case 2: Author is viewing the edit page of one of their novels
            elif self.action == 'retrieve' and self.request.query_params.get('view') == 'edit':
                # Check if the novel being retrieved belongs to the current user
                novel_pk = self.kwargs.get(self.lookup_field)
                if novel_pk and Novel.objects.filter(pk=novel_pk, author=user.author_profile).exists():
                    is_author_view = True
        
        context['is_author_view'] = is_author_view
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return NovelListSerializer
        if self.action == 'chapters':
            return ChapterEditSerializer
        return NovelDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'chapters']:
            self.permission_classes = [IsAuthorUserForWrite, IsAuthorOrReadOnly]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'author_profile'):
            serializer.save(author=self.request.user.author_profile)
        else:
            raise serializers.ValidationError("只有作者才能發表小說。")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def novel_analytics(request, pk):
    try:
        novel = Novel.objects.get(pk=pk)
    except Novel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if novel.author.user != request.user:
        return Response({'detail': '沒有權限。'}, status=status.HTTP_403_FORBIDDEN)

    chapters_analytics = Chapter.objects.filter(novel=novel).order_by('order')
    
    labels = [chapter.title for chapter in chapters_analytics]
    data = [chapter.views for chapter in chapters_analytics]

    return Response({
        'labels': labels,
        'data': data,
    })

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterEditSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChapterDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ChapterEditSerializer
        # For list action, including when mode=edit is present
        return ChapterSerializer

    def retrieve(self, request, *args, **kwargs):
        chapter_instance = self.get_object() # This gets the Chapter object

        # Increment views on the associated Novel
        novel_instance = chapter_instance.novel # Get the associated Novel object
        novel_instance.views += 1
        novel_instance.save(update_fields=['views'])

        # Serialize the Chapter instance
        serializer = self.get_serializer(chapter_instance)
        return Response(serializer.data)

    def get_queryset(self):
        novel_pk = self.kwargs.get('novel_pk')
        if novel_pk is None:
            return self.queryset.none() # 如果沒有 novel_pk，則不返回任何章節

        queryset = self.queryset.filter(novel_id=novel_pk)
        if 'volume_pk' in self.kwargs:
            queryset = queryset.filter(volume_id=self.kwargs['volume_pk'])
        return queryset

    def perform_create(self, serializer):
        novel = Novel.objects.get(pk=self.kwargs['novel_pk'])

        # 為了確保 'order' 在整本小說中是唯一的，我們總是基於小說本身來計算下一個 order
        last_chapter = Chapter.objects.filter(novel=novel).order_by('-order').first()
        
        next_order = (last_chapter.order + 1) if last_chapter else 1
        
        # 序列化器會自動處理 'volume' (如果有的話)
        serializer.save(novel=novel, order=next_order)




class ReadingProgressViewSet(viewsets.ModelViewSet):
    """
    處理使用者的閱讀進度與書架。
    - list: 獲取當前使用者的書架列表
    - create: 將小說加入書架 (或更新閱讀進度)
    - destroy: 將小說從書架移除
    """
    queryset = ReadingProgress.objects.all()
    serializer_class = ReadingProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        只返回當前登入使用者的閱讀進度。
        Use select_related to optimize fetching related novel and author data.
        """
        return ReadingProgress.objects.filter(user=self.request.user).select_related(
            'novel', 
            'novel__author', 
            'novel__author__user',
            'last_read_chapter'
        )

    def perform_create(self, serializer):
        """建立或更新閱讀進度。"""
        novel_id = self.request.data.get('novel')
        if not novel_id:
            raise serializers.ValidationError({'novel': '小說 ID 是必填的。'})
        
        # 檢查是否已經存在該小說的閱讀進度
        reading_progress, created = ReadingProgress.objects.get_or_create(
            user=self.request.user,
            novel_id=novel_id,
            defaults={'last_read_chapter': None} # 初始時沒有最後閱讀章節
        )
        
        # 如果是更新操作，則更新 last_read_chapter
        last_read_chapter_id = self.request.data.get('last_read_chapter')
        if last_read_chapter_id:
            try:
                chapter = Chapter.objects.get(id=last_read_chapter_id, novel_id=novel_id)
                reading_progress.last_read_chapter = chapter
                reading_progress.save()
            except Chapter.DoesNotExist:
                raise serializers.ValidationError({'last_read_chapter': '指定的章節不存在。'})
        
        # 如果是新建立的，或者只是加入書架，返回成功
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        """從書架移除。"""
        instance.delete()