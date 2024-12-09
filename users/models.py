# users/models
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定義用戶模型。
    """

    related_stores = models.ManyToManyField(
        'store.Store',
        blank=True,
        help_text="服務人員或管理員所關聯的多個店鋪",
        related_name="store_users"  # 反向查詢時的名稱
    )
    phone_number = models.CharField(
        max_length=15, blank=True, null=True,
        help_text="用戶的聯絡電話，例如手機號碼"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True,
        help_text="用戶頭像，存儲圖片文件的路徑"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="用戶創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="用戶資料的最後更新時間"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
