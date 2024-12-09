def get_client_ip(request):
    """
    從請求中提取用戶的真實 IP 地址。
    支援多層代理，優先取 X-Forwarded-For 的第一個 IP。
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '未知 IP')
    return ip
