from django.shortcuts import redirect
from django.urls import reverse


class SecurityCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 如果用戶已驗證，放行
        if request.session.get("security_verified", False):
            return self.get_response(request)

        # 如果請求的 URL 是驗證頁面，放行
        if request.path == reverse("security_check:check"):
            return self.get_response(request)

        # 否則，重定向到驗證頁面
        return redirect(reverse("security_check:check"))
