# novel_backend/core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import CustomUser, AuthorProfile, Novel, Chapter, Volume

# --- 內嵌管理介面 ---
class AuthorProfileInline(admin.StackedInline):
    model = AuthorProfile
    can_delete = False
    verbose_name_plural = '作者檔案'
    fields = ('pen_name', 'bio')

# --- 主要模型管理介面 ---
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'get_avatar')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email')
    
    inlines = [] # 預設無內嵌

    # 覆寫 get_inlines，動態決定是否顯示作者檔案的編輯區塊
    def get_inlines(self, request, obj=None):
        if obj and obj.role == CustomUser.Role.AUTHOR:
            return [AuthorProfileInline]
        return []

    # 覆寫 fieldsets，使佈局更清晰
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('個人資訊', {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        ('權限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('網站角色', {'fields': ('role',)}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )

    # 在列表頁顯示頭像預覽
    def get_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;" />', obj.avatar.url)
        return "無"
    get_avatar.short_description = '頭像'

@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'updated_at')
    list_filter = ('status', 'author')
    search_fields = ('title', 'author__pen_name', 'author__user__username')
    # 移除 ChapterInline，改為獨立管理
    inlines = [] 
    fieldsets = (
        ('基本資訊', {
            'fields': ('title', 'author', 'status')
        }),
        ('內容與封面', {
            'fields': ('description', 'cover_image')
        }),
    )

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'novel', 'volume', 'order')
    list_filter = ('novel', 'volume')
    search_fields = ('title', 'novel__title')
    # 使用 raw_id_fields 提高性能，方便選擇關聯物件
    raw_id_fields = ('novel', 'volume')
    list_editable = ('order',)

@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'novel', 'order')
    list_filter = ('novel',)
    search_fields = ('title', 'novel__title')
    raw_id_fields = ('novel',)
