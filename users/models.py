# users/models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    """
    自定義用戶模型。
    """

    related_stores = models.ManyToManyField(
        'Store', blank=True,
        help_text="服務人員或管理員所關聯的多個店鋪",
        related_name="store_users"  # 反向查詢用戶時的名稱
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


class Store(models.Model):
    """
    店鋪模型，用於記錄商家的店鋪信息。
    """
    merchant = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'role': 'merchant'},
        help_text="店鋪所屬的商家，用戶角色必須是 '商家'"
    )
    name = models.CharField(
        max_length=150, help_text="店鋪名稱，例如 '幸福剪髮'"
    )
    location = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="店鋪的具體地址"
    )
    phone = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="店鋪的聯絡電話"
    )
    opening_time = models.TimeField(
        help_text="店鋪營業的開始時間，例如 '09:00'"
    )
    closing_time = models.TimeField(
        help_text="店鋪營業的結束時間，例如 '18:00'"
    )
    business_days = models.JSONField(
        default=list,
        help_text="店鋪的營業日（JSON格式，例如 ['Monday', 'Tuesday'])"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="店鋪是否啟用，預設為啟用狀態"
    )
    created_at = models.DateTimeField(
        default=now,
        help_text="店鋪的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="店鋪的最後更新時間"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_stores", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_stores", help_text="最後修改人員"
    )

    class Meta:
        unique_together = ('merchant', 'name')  # 商家內店鋪名稱唯一

    def __str__(self):
        return f"{self.name} ({self.merchant.username})"


class RoleCategory(models.Model):
    """
    角色分類模型，用於動態管理角色的分類。
    """
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE,
        help_text="該分類所屬的店鋪"
    )
    name = models.CharField(
        max_length=50, help_text="分類名稱，例如 '技術類' 或 '管理類'"
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="分類的描述，例如該分類適用於哪些角色"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="分類是否啟用，預設為啟用狀態"
    )
    created_at = models.DateTimeField(
        default=now,
        help_text="該分類的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="該分類的最後更新時間"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_role_categories", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_role_categories", help_text="最後修改人員"
    )

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class StaffRole(models.Model):
    """
    服務人員角色模型，用於記錄服務人員的具體角色，例如 '按摩師' 或 '健身教練'。
    """
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE,
        help_text="該角色所屬的店鋪"
    )
    category = models.ForeignKey(
        'RoleCategory', on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="角色的分類，例如 '技術類'"
    )
    name = models.CharField(
        max_length=50, help_text="角色名稱，例如 '按摩師'"
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="角色的描述，例如工作內容或技能要求"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="角色是否啟用，預設為啟用狀態"
    )
    created_at = models.DateTimeField(
        default=now,
        help_text="該角色的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="該角色的最後更新時間"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_staff_roles", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_staff_roles", help_text="最後修改人員"
    )

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class Staff(models.Model):
    """
    服務人員模型，用於記錄每位服務人員的基本信息和所屬角色。
    """
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE,
        help_text="服務人員所屬的店鋪"
    )
    name = models.CharField(
        max_length=150, help_text="服務人員的姓名"
    )
    user_account = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'staff'},
        help_text="服務人員對應的用戶帳號（可選）"
    )
    role = models.ForeignKey(
        'StaffRole', on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="服務人員的角色，例如 '按摩師'"
    )
    phone = models.CharField(
        max_length=15, blank=True, null=True,
        help_text="服務人員的聯絡電話"
    )
    expertise = models.TextField(
        blank=True, null=True,
        help_text="服務人員的專長描述，例如 '擅長足底按摩'"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="服務人員是否仍在職，預設為在職狀態"
    )
    created_at = models.DateTimeField(
        default=now,
        help_text="服務人員的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="服務人員的最後更新時間"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_staff", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_staff", help_text="最後修改人員"
    )

    def __str__(self):
        return f"{self.name} ({self.role.name if self.role else '未指定角色'}) - {self.store.name}"
