from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # 店鋪管理
    path('', views.store_list, name='store_list'),  # 店鋪列表

    # 角色分類管理
    path('roles/', views.role_category_list,
         name='role_category_list'),  # 角色分類列表

    # 服務管理
    path('services/', views.service_list, name='service_list'),  # 服務列表

    # 人員管理
    path('staff/', views.staff_list, name='staff_list'),  # 服務人員列表

    # 預約管理
    path('appointments/', views.appointment_list,
         name='appointment_list'),  # 預約管理列表
]
