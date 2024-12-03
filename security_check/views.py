from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
import requests


def check_security(request):
    """
    驗證頁面邏輯。
    如果是 GET 請求，顯示驗證頁面。
    如果是 POST 請求，處理驗證邏輯。
    """
    if request.method == "POST":
        # Turnstile 驗證 Token
        turnstile_token = request.POST.get("cf-turnstile-response")

        if not turnstile_token:
            return JsonResponse({"error": "驗證失敗：Token 缺失"}, status=400)

        # 發送驗證請求給 Turnstile API
        verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        payload = {
            "secret": settings.SECURITY_CHECK_SECRET_KEY,
            "response": turnstile_token,
            "remoteip": get_client_ip(request),
        }
        response = requests.post(verify_url, data=payload)
        result = response.json()

        if result.get("success", False):
            # 驗證成功，設置 session 狀態
            request.session["security_verified"] = True
            return redirect("/")  # 成功後跳轉至首頁

        # 驗證失敗，返回錯誤
        return JsonResponse({"error": "驗證失敗，請重新嘗試"}, status=400)

    # GET 請求，顯示驗證頁面，傳遞 IP 給前端
    client_ip = get_client_ip(request)
    return render(request, "security_check.html", {"client_ip": client_ip})


def get_client_ip(request):
    """
    獲取用戶的 IP 地址，用於向 Turnstile API 傳遞 remoteip。
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
