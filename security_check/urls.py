from django.urls import path
from . import views

app_name = "security_check"

urlpatterns = [
    path("", views.check_security, name="check"),  # 驗證頁面
]
