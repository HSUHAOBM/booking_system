from django.urls import path
from . import views
from django.http import HttpResponse


# 暫時的顧客儀表板視圖
def customer_dashboard(request):
    return HttpResponse("顧客儀表板")


def admin_dashboard(request):
    return HttpResponse("admin_dashboard儀表板")


app_name = "users"

urlpatterns = [
    path('register/', views.register, name='register'),  # 註冊頁面
    path('login/', views.login, name='login'),  # 登入頁面
    path('logout/', views.logout, name='logout'),  # 登出（可選）

    path('customer_dashboard/', customer_dashboard, name='customer_dashboard'),

    path('dashboard/', views.dashboard, name='dashboard'),  # 登入後的主頁
]
