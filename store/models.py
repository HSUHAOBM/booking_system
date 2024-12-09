from django.db import models
from django.utils.timezone import now


class Store(models.Model):
    """
    店鋪模型，用於記錄商家的店鋪信息。
    """
    merchant = models.ForeignKey(
        'users.User',  # 使用字符串引用避免循環導入
        on_delete=models.CASCADE,
        related_name="owned_stores",  # 用戶名下的店鋪
        related_query_name="store",  # 查詢時可用 user.store_set
        help_text="店鋪所屬的商家"
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
        auto_now_add=True,
        help_text="店鋪的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="店鋪的最後更新時間"
    )
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_stores", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_stores", help_text="最後修改人員"
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
        auto_now_add=True,
        help_text="該分類的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="該分類的最後更新時間"
    )
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_role_categories", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_role_categories", help_text="最後修改人員"
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
        auto_now_add=True,
        help_text="該角色的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="該角色的最後更新時間"
    )
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_staff_roles", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_staff_roles", help_text="最後修改人員"
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
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
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
        auto_now_add=True,
        help_text="服務人員的創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="服務人員的最後更新時間"
    )
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_staff", help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_staff", help_text="最後修改人員"
    )

    def __str__(self):
        return f"{self.name} ({self.role.name if self.role else '未指定角色'}) - {self.store.name}"


class ServiceCategory(models.Model):
    """
    服務分類模型，支持動態管理服務的分類。
    """
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE,
        help_text="所屬店鋪"
    )
    name = models.CharField(max_length=50, help_text="分類名稱，例如 '剪髮'")
    description = models.TextField(blank=True, null=True, help_text="分類描述")
    is_active = models.BooleanField(default=True, help_text="分類是否啟用")
    created_at = models.DateTimeField(auto_now_add=True, help_text="創建時間")
    updated_at = models.DateTimeField(auto_now=True, help_text="最後修改時間")
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_service_categories",
        help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_service_categories",
        help_text="最後修改人員"
    )

    class Meta:
        unique_together = ('store', 'name')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class Service(models.Model):
    """
    服務模型，記錄商家提供的服務信息。
    """
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE,
        help_text="服務所屬的店鋪"
    )
    name = models.CharField(max_length=150, help_text="服務名稱，例如 '男生剪髮'")
    category = models.ForeignKey(
        'ServiceCategory', on_delete=models.SET_NULL, null=True, blank=True, help_text="服務分類"
    )
    description = models.TextField(blank=True, null=True, help_text="服務的詳細描述")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="服務價格"
    )
    duration = models.IntegerField(help_text="服務時長（分鐘）")
    staff = models.ManyToManyField(
        'Staff', related_name='services', help_text="可以提供該服務的服務人員"
    )
    is_active = models.BooleanField(default=True, help_text="服務是否啟用")
    created_at = models.DateTimeField(auto_now_add=True, help_text="創建時間")
    updated_at = models.DateTimeField(auto_now=True, help_text="最後修改時間")
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_services",
        help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_services",
        help_text="最後修改人員"
    )

    class Meta:
        unique_together = ('store', 'name')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class WorkSchedule(models.Model):
    """
    服務人員排班模型，記錄服務人員的每日工作日程。
    """
    staff = models.ForeignKey(
        'Staff', on_delete=models.CASCADE, help_text="服務人員"
    )
    date = models.DateField(help_text="排班日期")
    start_time = models.TimeField(help_text="排班開始時間")
    end_time = models.TimeField(help_text="排班結束時間")
    is_active = models.BooleanField(default=True, help_text="排班是否啟用")
    created_at = models.DateTimeField(auto_now_add=True, help_text="創建時間")
    updated_at = models.DateTimeField(auto_now=True, help_text="最後修改時間")
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_work_schedules",
        help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_work_schedules",
        help_text="最後修改人員"
    )

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.staff.name} - {self.date} ({self.start_time} ~ {self.end_time})"


class TimeSlot(models.Model):
    """
    時段模型，記錄具體可預約的時間段。
    """
    schedule = models.ForeignKey(
        'WorkSchedule', on_delete=models.CASCADE, help_text="所屬排班"
    )
    service = models.ForeignKey(
        'Service', on_delete=models.CASCADE, help_text="時段對應的服務"
    )
    start_time = models.DateTimeField(help_text="時段開始時間")
    end_time = models.DateTimeField(help_text="時段結束時間")
    max_capacity = models.IntegerField(default=1, help_text="時段最大預約人數")
    is_active = models.BooleanField(default=True, help_text="時段是否有效")
    created_at = models.DateTimeField(auto_now_add=True, help_text="創建時間")
    updated_at = models.DateTimeField(auto_now=True, help_text="最後修改時間")
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_time_slots",
        help_text="創建人員"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_time_slots",
        help_text="最後修改人員"
    )

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.service.name} ({self.schedule.staff.name}): {self.start_time} - {self.end_time}"
