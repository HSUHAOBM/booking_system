from django.shortcuts import render

# Create your views here.


def register(request):
    """
    處理註冊頁面的請求。
    """
    return render(request, "users/register.html")


def login(request):
    """
    處理登入的請求。
    """
    return render(request, "users/login.html")


def logout(request):
    """
    處理登出的請求。
    """
    return render(request, "users/logout.html")
