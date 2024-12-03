from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as auth_login, get_user_model, logout as auth_logout

# 使用自訂的用戶模型
User = get_user_model()


def validate_password_strength(password):
    """
    驗證密碼的強度：長度、大小寫字母和數字要求。
    """
    if len(password) < 12:
        raise ValidationError("密碼長度至少為 12 個字符。")
    if not any(char.isupper() for char in password):
        raise ValidationError("密碼需包含至少一個大寫字母。")
    if not any(char.islower() for char in password):
        raise ValidationError("密碼需包含至少一個小寫字母。")
    if not any(char.isdigit() for char in password):
        raise ValidationError("密碼需包含至少一個數字。")


def register(request):
    """
    處理註冊邏輯：用戶自定義 username，並以 email 作為登入憑據
    """
    if request.method == "POST":
        username = request.POST.get('username', '')  # 預設為空字串
        email = request.POST.get('email', '')  # 預設為空字串
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        # 驗證密碼一致性
        if password != confirm_password:
            messages.error(request, "密碼與確認密碼不一致。")
            return render(request, "users/register.html", {'username': username, 'email': email})
        # 驗證密碼強度
        try:
            validate_password_strength(password)
        except ValidationError as e:
            messages.error(request, e.messages[0])  # 顯示第一條錯誤訊息
            return render(request, "users/register.html", {'username': username, 'email': email})

        # 檢查 username 是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, "該使用者名稱已被使用，請嘗試其他名稱。")
            return render(request, "users/register.html", {'username': username, 'email': email})

        # 檢查 Email 是否已存在
        if User.objects.filter(email=email).exists():
            messages.error(request, "該信箱已被註冊。")
            return render(request, "users/register.html", {'username': username, 'email': email})

        # 創建用戶
        try:
            user = User.objects.create_user(
                username=username, email=email, password=password)
            user.save()
            messages.success(request, "註冊成功，請登入！")
            return redirect('users:login')
        except Exception as e:
            messages.error(request, f"註冊失敗，請稍後再試。錯誤訊息：{str(e)}")
            return render(request, "users/register.html", {'username': username, 'email': email})

    return render(request, "users/register.html", {'username': '', 'email': ''})


def login(request):
    """
    使用 Email 和密碼進行驗證並登入。
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # 檢查是否有空欄
        if not email or not password:
            messages.error(request, "請輸入信箱和密碼")
            return render(request, "users/login.html", {"email": email})

        user, error_message = _authenticate_user(email, password)  # 獲取用戶和錯誤訊息
        if user:
            return _redirect_user_by_role(request, user)
        else:
            if error_message:
                messages.error(request, error_message)  # 添加錯誤訊息
            return render(request, "users/login.html", {"email": email})

    # GET 請求，渲染空白表單
    return render(request, "users/login.html", {"email": ""})


def _authenticate_user(email, password):
    """
    驗證用戶的 Email 和密碼，返回用戶或 None，並附帶錯誤訊息。
    """
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user, None  # 驗證成功
        else:
            return None, "密碼錯誤，請重新嘗試。"  # 密碼錯誤
    except User.DoesNotExist:
        return None, "該信箱尚未註冊。"  # 用戶不存在


def _redirect_user_by_role(request, user):
    """
    根據用戶角色重定向到相應的頁面。
    """
    auth_login(request, user)
    messages.success(request, "登入成功！")

    if user.role in ["merchant", "staff", "admin"]:
        return redirect("users:admin_dashboard")
    elif user.role == "customer":
        return redirect("users:customer_dashboard")
    else:
        messages.error(request, "無法識別用戶角色，請聯繫管理員。")
        return redirect("home")


def logout(request):
    """
    處理登出的請求。
    """
    security_verified = request.session.get(
        "security_verified", False)  # 保存驗證狀態
    auth_logout(request)
    if security_verified:  # 如果之前驗證過，重新設置
        request.session["security_verified"] = True
    messages.success(request, "您已成功登出！")
    return redirect("users:login")
