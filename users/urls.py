from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('register/', views.register, name='register'),  # 註冊頁面
    path('login/', views.login, name='login'),  # 登入頁面
    path('logout/', views.logout, name='logout'),  # 登出（可選）
]
