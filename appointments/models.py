# appointments/models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Appointment(models.Model):
    """
    預約模型，記錄客人的預約信息。
    """
    customer = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        limit_choices_to={'role': 'customer'},
        help_text="關聯到預約的客人，用戶角色必須是 '客人'"
    )
    service = models.ForeignKey(
        'services.Service', on_delete=models.CASCADE,
        help_text="關聯到預約的服務，例如剪髮、按摩等"
    )
    staff = models.ForeignKey(
        'users.Staff', on_delete=models.CASCADE,
        help_text="關聯到提供服務的服務人員"
    )
    timeslot = models.OneToOneField(
        'services.TimeSlot', on_delete=models.CASCADE, related_name="appointments",
        help_text="關聯到具體的預約時間段"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待確認'),
            ('confirmed', '已確認'),
            ('canceled', '已取消'),
            ('missed', '未出席'),
        ],
        default='pending',
        help_text="預約狀態，例如待確認、已確認、已取消或未出席"
    )
    note = models.TextField(
        blank=True, null=True,
        help_text="客人在預約時提交的備註或特殊要求"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="預約創建時間"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="預約最後修改時間"
    )
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_appointments",
        help_text="記錄創建此預約的用戶"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_appointments",
        help_text="記錄最後修改此預約的用戶"
    )

    def __str__(self):
        return f"{self.customer.username} -> {self.staff.name}: {self.service.name} ({self.status})"


class AppointmentHistory(models.Model):
    """
    預約歷史模型，記錄預約的狀態變更。
    """
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='history',
        help_text="關聯到對應的預約"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待確認'),
            ('confirmed', '已確認'),
            ('canceled', '已取消'),
            ('missed', '未出席'),
        ],
        help_text="預約變更後的狀態"
    )
    updated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="進行狀態變更的用戶"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="狀態更新時間"
    )

    def __str__(self):
        return f"{self.appointment} - {self.status} @ {self.timestamp}"


class Feedback(models.Model):
    """
    評價模型，記錄客人的服務評價。
    """
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE,
        help_text="關聯到對應的預約"
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, message="評分不能低於 1 分"),
            MaxValueValidator(5, message="評分不能高於 5 分"),
        ],
        help_text="評分（1-5）"
    )
    comment = models.TextField(
        blank=True, null=True,
        help_text="評價內容，例如對服務的反饋"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="評價創建時間"
    )

    def __str__(self):
        return f"{self.appointment.customer.username} - Rating: {self.rating}"


class Notification(models.Model):
    """
    通知模型，記錄商家和客人的通知信息。
    """
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        help_text="接收通知的用戶"
    )
    message = models.TextField(
        help_text="通知的具體內容"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="通知是否已讀"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="通知創建時間"
    )

    def __str__(self):
        return f"To {self.user.username}: {self.message}"
