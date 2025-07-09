# novel_backend/core/serializers.py
from datetime import timedelta
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, AuthorProfile, Novel, Chapter, ReadingProgress, Volume # 引入 ReadingProgress 和 Volume

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    remember_me = serializers.BooleanField(write_only=True, required=False, default=False)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role
        token['test_field'] = 'serializer_test'
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        # Set token lifetimes based on remember_me
        remember_me = attrs.get('remember_me', False)
        if remember_me:
            access_lifetime = timedelta(days=1)
            refresh_lifetime = timedelta(days=30)
        else:
            access_lifetime = timedelta(minutes=60)
            refresh_lifetime = timedelta(days=7)

        refresh.set_exp(lifetime=refresh_lifetime)
        
        access = refresh.access_token
        access.set_exp(lifetime=access_lifetime)

        data['refresh'] = str(refresh)
        data['access'] = str(access)

        return data

# ===================================================================
#  使用者 (User) & 個人檔案 (Profile) Serializers
# ===================================================================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """用於新使用者註冊"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """
    用於「個人設定」頁面，讓使用者更新自己的資料。
    """
    # 透過 source 直接訪問關聯的 AuthorProfile 欄位
    pen_name = serializers.CharField(source='author_profile.pen_name', required=False, allow_blank=True)
    bio = serializers.CharField(source='author_profile.bio', required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        # 我們從 CustomUser 出發，可以訪問 avatar, username 等
        # 也可以透過 source='author_profile.field' 訪問作者資料
        fields = ['id', 'username', 'email', 'avatar', 'role', 'pen_name', 'bio']
        read_only_fields = ['username', 'email', 'role']

    def update(self, instance, validated_data):
        # instance 在這裡是 CustomUser 物件
        
        # 如果有 'author_profile' 相關的資料，則更新 AuthorProfile
        if 'author_profile' in validated_data:
            profile_data = validated_data.pop('author_profile')
            profile_instance = instance.author_profile
            
            # 更新 AuthorProfile 的欄位
            profile_instance.pen_name = profile_data.get('pen_name', profile_instance.pen_name)
            profile_instance.bio = profile_data.get('bio', profile_instance.bio)
            profile_instance.save()
        
        # 更新 CustomUser 的欄位 (主要是 avatar)
        # super().update 會處理 validated_data 中剩餘的欄位
        return super().update(instance, validated_data)


# ===================================================================
#  作者 (Author) & 小說 (Novel) 的公開展示 Serializers
# ===================================================================

class AuthorSummarySerializer(serializers.ModelSerializer):
    """
    【修正版】
    用於在小說卡片上顯示最精簡的作者資訊。
    """
    # 告訴 DRF 'username' 和 'avatar' 要從關聯的 'user' 物件中獲取
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = AuthorProfile
        fields = ['user_id', 'username', 'pen_name', 'avatar']

class SimpleNovelSerializer(serializers.ModelSerializer):
    """用於在作者公開頁上顯示小說列表，避免循環引用"""
    class Meta:
        model = Novel
        fields = ['id', 'title', 'cover_image', 'status', 'updated_at', 'description']

class AuthorDetailSerializer(serializers.ModelSerializer):
    """
    用於作者的公開頁面，包含完整的個人檔案和其所有小說的列表。
    """
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    novels = SimpleNovelSerializer(many=True, read_only=True) # 使用 related_name 'novels'

    class Meta:
        model = AuthorProfile
        fields = ['user_id', 'username', 'pen_name', 'bio', 'avatar', 'novels']

class ChapterSerializer(serializers.ModelSerializer):
    """用於在小說詳情頁顯示章節列表"""
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'published_at', 'volume', 'status']

class ChapterDetailSerializer(serializers.ModelSerializer):
    """用於顯示單一章節的詳細內容，包含內容本身"""
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'order', 'published_at', 'views', 'novel', 'volume', 'status']

class NestedChapterSerializer(serializers.ModelSerializer):
    """用於在 Volume 內嵌套顯示章節"""
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'published_at']

class VolumeSerializer(serializers.ModelSerializer):
    """Serializes a volume and its chapters, filtering chapters based on context."""
    chapters = serializers.SerializerMethodField()

    class Meta:
        model = Volume
        fields = ['id', 'title', 'order', 'chapters']
        read_only_fields = ['order']

    def get_chapters(self, obj):
        is_author_view = self.context.get('is_author_view', False)
        
        # Access the prefetched chapters if available, otherwise query
        chapters_queryset = obj.chapters.all()

        if not is_author_view:
            chapters_queryset = chapters_queryset.filter(status=Chapter.Status.PUBLISHED)
        
        # The chapters are already ordered by the prefetch in the view
        serializer = NestedChapterSerializer(chapters_queryset, many=True)
        return serializer.data

class NovelDetailSerializer(serializers.ModelSerializer):
    """Serializes novel details, filtering chapters based on context."""
    author = AuthorSummarySerializer(read_only=True)
    # Use the new attribute 'volumes_ordered' from the prefetch
    volumes = VolumeSerializer(source='volumes_ordered', many=True, read_only=True)
    chapters_without_volume = serializers.SerializerMethodField()

    class Meta:
        model = Novel
        fields = [
            'id', 'title', 'author', 'description', 'cover_image', 'status', 
            'volumes', 'chapters_without_volume', 'created_at', 'updated_at'
        ]

    def get_chapters_without_volume(self, obj):
        is_author_view = self.context.get('is_author_view', False)
        # obj.chapters_without_volume is a list from the prefetch
        chapters_list = obj.chapters_without_volume

        if not is_author_view:
            chapters_list = [ch for ch in chapters_list if ch.status == Chapter.Status.PUBLISHED]

        serializer = ChapterSerializer(chapters_list, many=True)
        return serializer.data

class NovelListSerializer(NovelDetailSerializer):
    """Inherits from NovelDetailSerializer to ensure consistent chapter filtering."""
    pass


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def create(self, validated_data):
        # This serializer is not for creating model instances,
        # but for validating the uploaded file.
        # The view will handle the file saving and URL generation.
        return validated_data


class ChapterEditSerializer(serializers.ModelSerializer):
    """用於作者編輯章節"""
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'order', 'volume', 'status']
        read_only_fields = ['id', 'order']


class SimpleNovelForReadingProgressSerializer(serializers.ModelSerializer):
    """A lightweight serializer for novels in the reading progress list."""
    author = AuthorSummarySerializer(read_only=True)
    class Meta:
        model = Novel
        fields = ['id', 'title', 'cover_image', 'author', 'status']


class ReadingProgressSerializer(serializers.ModelSerializer):
    novel_detail = SimpleNovelForReadingProgressSerializer(source='novel', read_only=True)
    last_read_chapter_detail = ChapterSerializer(source='last_read_chapter', read_only=True)

    class Meta:
        model = ReadingProgress
        fields = ['id', 'novel', 'last_read_chapter', 'added_to_bookshelf_at', 'novel_detail', 'last_read_chapter_detail']
        read_only_fields = ['user', 'added_to_bookshelf_at', 'novel_detail', 'last_read_chapter_detail']
