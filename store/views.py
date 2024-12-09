from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# 店鋪管理


@login_required
def store_list(request):
    return render(request, 'store/store_list.html')

# 角色分類管理


@login_required
def role_category_list(request):
    return render(request, 'store/role_category_list.html')

# 服務管理


@login_required
def service_list(request):
    return render(request, 'store/service_list.html')

# 人員管理


@login_required
def staff_list(request):
    return render(request, 'store/staff_list.html')

# 預約管理


@login_required
def appointment_list(request):
    return render(request, 'store/appointment_list.html')
