# services/models
from django.db import models
from django.utils.timezone import now


class ServiceCategory(models.Model):
    """
    服務分類模型，支持動態管理服務的分類。
    """
    store = models.ForeignKey(
        'users.Store', on_delete=models.CASCADE,
        help_text="所屬店鋪"
    )
    name = models.CharField(max_length=50, help_text="分類名稱，例如 '剪髮'")
    description = models.TextField(blank=True, null=True, help_text="分類描述")
    is_active = models.BooleanField(default=True, help_text="分類是否啟用")
    created_at = models.DateTimeField(default=now, help_text="創建時間")
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
        unique_together = ('store', 'name')  # 確保同一店鋪下分類名稱唯一
        ordering = ['-created_at']  # 按創建時間降序排列

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class Service(models.Model):
    """
    服務模型，記錄商家提供的服務信息。
    """
    store = models.ForeignKey(
        'users.Store', on_delete=models.CASCADE, help_text="服務所屬的店鋪"
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
        'users.Staff', related_name='services', help_text="可以提供該服務的服務人員"
    )
    is_active = models.BooleanField(default=True, help_text="服務是否啟用")
    created_at = models.DateTimeField(default=now, help_text="創建時間")
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
        unique_together = ('store', 'name')  # 確保同一店鋪下服務名稱唯一
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class WorkSchedule(models.Model):
    """
    服務人員排班模型，記錄服務人員的每日工作日程。
    """
    staff = models.ForeignKey(
        'users.Staff', on_delete=models.CASCADE, help_text="服務人員"
    )
    date = models.DateField(help_text="排班日期")
    start_time = models.TimeField(help_text="排班開始時間")
    end_time = models.TimeField(help_text="排班結束時間")
    is_active = models.BooleanField(default=True, help_text="排班是否啟用")
    created_at = models.DateTimeField(default=now, help_text="創建時間")
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
        WorkSchedule, on_delete=models.CASCADE, help_text="所屬排班"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, help_text="時段對應的服務"
    )
    start_time = models.DateTimeField(help_text="時段開始時間")
    end_time = models.DateTimeField(help_text="時段結束時間")
    max_capacity = models.IntegerField(default=1, help_text="時段最大預約人數")
    is_active = models.BooleanField(default=True, help_text="時段是否有效")
    created_at = models.DateTimeField(default=now, help_text="創建時間")
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
