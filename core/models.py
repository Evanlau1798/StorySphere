# novel_backend/core/models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        READER = "READER", "讀者"
        AUTHOR = "AUTHOR", "作者"
        ADMIN = "ADMIN", "管理員"

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.READER,
        verbose_name="角色"
    )
    
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True, 
        verbose_name="頭像"
    )
    
    discord_webhook_url = models.URLField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name="Discord Webhook URL"
    )

    def __str__(self):
        return self.username

class AuthorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='author_profile'
    )
    pen_name = models.CharField(max_length=100, blank=True, verbose_name="筆名")
    bio = models.TextField(blank=True, verbose_name="個人簡介")

    def __str__(self):
        # 顯示筆名，如果為空則顯示使用者名稱
        display_name = self.pen_name or self.user.username
        return f"{display_name} (作者檔案)"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if instance.role == CustomUser.Role.AUTHOR:
        AuthorProfile.objects.get_or_create(user=instance)

class Novel(models.Model):
    class Status(models.TextChoices):
        ONGOING = "ONGOING", "連載中"
        COMPLETED = "COMPLETED", "已完結"
        HIATUS = "HIATUS", "休刊中"

    class Category(models.TextChoices):
        FANTASY = "FANTASY", "奇幻"
        SCIFI = "SCIFI", "科幻"
        ROMANCE = "ROMANCE", "言情"
        URBAN = "URBAN", "都市"
        HISTORY = "HISTORY", "歷史"
        MARTIAL = "MARTIAL", "武俠"
        OTHERS = "OTHERS", "其他"

    title = models.CharField(max_length=255, verbose_name="書名")
    author = models.ForeignKey(
        AuthorProfile, 
        on_delete=models.CASCADE, 
        related_name='novels', 
        verbose_name="作者"
    )
    description = models.TextField(verbose_name="簡介")
    cover_image = models.ImageField(upload_to='novel_covers/', null=True, blank=True, verbose_name="封面圖片")
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.ONGOING, verbose_name="狀態")
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.OTHERS, verbose_name="分類")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最後更新時間")
    views = models.PositiveIntegerField(default=0, verbose_name="總觀看次數")

    def __str__(self):
        return self.title

class Volume(models.Model):
    novel = models.ForeignKey(
        Novel,
        on_delete=models.CASCADE,
        related_name='volumes',
        verbose_name="所屬小說"
    )
    title = models.CharField(max_length=255, verbose_name="卷標題")
    description = models.TextField(verbose_name="簡介", blank=True)
    cover_image = models.ImageField(upload_to='volume_covers/', null=True, blank=True, verbose_name="卷封面")
    order = models.PositiveIntegerField(verbose_name="卷順序")

    class Meta:
        unique_together = ('novel', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.novel.title} - Volume {self.order}: {self.title}"

class Chapter(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "草稿"
        PUBLISHED = "PUBLISHED", "已發布"

    novel = models.ForeignKey(
        Novel, 
        on_delete=models.CASCADE, 
        related_name='chapters', 
        verbose_name="所屬小說"
    )
    volume = models.ForeignKey(
        Volume,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chapters',
        verbose_name="所屬卷"
    )
    title = models.CharField(max_length=255, verbose_name="章節標題")
    content = models.TextField(verbose_name="內容", default='')
    order = models.PositiveIntegerField(verbose_name="章節順序")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="發布時間")
    views = models.PositiveIntegerField(default=0, verbose_name="觀看次數")
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.DRAFT, 
        verbose_name="狀態"
    )
    
    class Meta:
        unique_together = ('novel', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.novel.title} - Chapter {self.order}: {self.title}"


class ReadingProgress(models.Model):
    """追蹤使用者的閱讀進度與書架"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_progresses'
    )
    novel = models.ForeignKey(
        Novel,
        on_delete=models.CASCADE,
        related_name='reading_progresses'
    )
    last_read_chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    added_to_bookshelf_at = models.DateTimeField(auto_now_add=True, verbose_name="加入書架時間")

    class Meta:
        unique_together = ('user', 'novel')
        ordering = ['-added_to_bookshelf_at']

    def __str__(self):
        return f"{self.user.username} is reading {self.novel.title}"