from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as auth_login, get_user_model, logout as auth_logout
from django.db import transaction
import logging
from booking_system.utils import get_client_ip
from django.utils.html import escape
import re
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

# 使用自訂的用戶模型
User = get_user_model()


logger = logging.getLogger(__name__)


def validate_mobile_number(phone_number):
    """
    驗證手機號碼格式：台灣手機號碼需符合 09xxxxxxxx 格式
    """
    return re.match(r'^09\d{8}$', phone_number)


def is_unique_username(username):
    """檢查使用者名稱是否唯一"""
    return not User.objects.filter(username=username).exists()


def is_unique_email(email):
    """檢查電子郵件是否唯一"""
    return not User.objects.filter(email=email).exists()


def validate_password_strength(password):
    """
    驗證密碼的強度：長度、大小寫字母和數字要求
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
    """通用註冊邏輯"""
    if request.method == "POST":
        username = escape(request.POST.get('username', '').strip())
        email = escape(request.POST.get('email', '').strip())
        mobile_number = request.POST.get('phoneNumber', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        ip_address = request.META.get('REMOTE_ADDR', '')  # 提取 IP 地址

        logger.info(
            f"收到註冊請求: username={username}, email={email}, ip={ip_address}")

        # 驗證手機號碼
        if not validate_mobile_number(mobile_number):
            messages.error(request, "請輸入有效的手機號碼（格式：09xxxxxxxx）。")
            return render(request, 'users/register.html', {
                'username': username, 'email': email, 'phone_number': mobile_number
            })

        # 密碼一致性檢查
        if password != confirm_password:
            messages.error(request, "密碼與確認密碼不一致。")
            return render(request, 'users/register.html', {
                'username': username, 'email': email, 'phone_number': mobile_number
            })

        # 密碼強度檢查
        try:
            validate_password_strength(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'users/register.html', {
                'username': username, 'email': email, 'phone_number': mobile_number
            })

        # 唯一性檢查
        if not is_unique_username(username):
            messages.error(request, "該使用者名稱已被使用。")
            return render(request, 'users/register.html', {
                'username': username, 'email': email, 'phone_number': mobile_number
            })
        if not is_unique_email(email):
            messages.error(request, "該電子郵件已被註冊。")
            return render(request, 'users/register.html', {
                'username': username, 'email': email, 'phone_number': mobile_number
            })

        # 創建用戶
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=mobile_number,
            )
            messages.success(request, "註冊成功，請登入！")
            logger.info(
                f"用戶註冊成功: username={username}, email={email}, ip={ip_address}")
            return redirect('users:login')
        except IntegrityError:
            messages.error(request, "註冊失敗，請稍後再試。")
            logger.error(
                f"用戶註冊失敗（數據庫錯誤）: username={username}, email={email}, ip={ip_address}")
        except Exception as e:
            messages.error(request, f"註冊失敗，請稍後再試。錯誤訊息：{str(e)}")
            logger.exception(f"用戶註冊失敗（未知錯誤）錯誤訊息：{str(e)}")

    return render(request, 'users/register.html')


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

        # 驗證用戶
        user, error_message = _authenticate_user(email, password)  # 獲取用戶和錯誤訊息
        if user:
            auth_login(request, user)  # 登入用戶
            return redirect("users:dashboard")
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
            return None, "信箱或密碼不正確"
    except User.DoesNotExist:
        return None, "信箱或密碼不正確"


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


@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')
