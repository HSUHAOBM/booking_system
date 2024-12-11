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
    # 註冊、登入與登出
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # 使用者儀表板
    path('customer_dashboard/', customer_dashboard, name='customer_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),  # 登入後的主頁

    # 帳號管理中心
    path('account_center', views.account_center, name='account_center'),

    # 隱私設定
    path('roles/', views.privacy_settings, name='privacy_settings'),

    # 協助與支援
    path('services/', views.support_help, name='support_help'),


]
