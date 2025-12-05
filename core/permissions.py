# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorOrReadOnly(BasePermission):
    """
    允許任何人讀取，但只有該物件的作者才能寫入。
    """
    def has_object_permission(self, request, view, obj):
        # 讀取請求 (GET, HEAD, OPTIONS) 總是允許
        if request.method in SAFE_METHODS:
            return True
        
        # 寫入請求需要檢查物件的作者是否為當前登入的使用者。
        # obj 是 Novel 或 Chapter 實例，obj.author 是 AuthorProfile 實例。
        # 我們需要比對 AuthorProfile 關聯的 user 和 request.user。
        if not request.user.is_authenticated:
            return False
            
        # 處理 Novel 物件
        if hasattr(obj, 'author') and hasattr(obj.author, 'user'):
            return obj.author.user == request.user
        
        # 處理 Chapter 物件 (透過 novel 關聯)
        if hasattr(obj, 'novel') and hasattr(obj.novel.author, 'user'):
            return obj.novel.author.user == request.user
            
        return False

class IsAuthorUserForWrite(BasePermission):
    """
    對於安全的讀取方法 (GET)，允許任何人訪問。
    對於不安全的寫入方法 (POST, PUT, PATCH, DELETE)，只允許角色為 'AUTHOR' 的使用者訪問。
    """
    def has_permission(self, request, view):
        # 如果是讀取請求，直接放行
        if request.method in SAFE_METHODS:
            return True
        
        # 如果是寫入請求，檢查使用者是否已登入且角色為 'AUTHOR'
        return request.user and request.user.is_authenticated and request.user.role == 'AUTHOR'

class IsAdminRole(BasePermission):
    """
    只允許角色為 'ADMIN' 的使用者訪問。
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'