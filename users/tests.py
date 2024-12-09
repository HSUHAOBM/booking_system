from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
import logging

# 使用自訂的用戶模型
User = get_user_model()


class RegisterCustomerTest(TestCase):
    def setUp(self):
        """
        初始化測試環境。
        """
        self.logger = logging.getLogger('users.views')
        self.previous_log_level = self.logger.level
        self.logger.setLevel(logging.CRITICAL)  # 禁用低於 CRITICAL 的日誌

        session = self.client.session
        session["security_verified"] = True
        session.save()

    def test_successful_registration(self):
        """
        測試成功註冊的情境。
        """
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phoneNumber': '0912345678',
            'password': 'Aa1234567890',
            'confirmPassword': 'Aa1234567890',
        })
        self.assertRedirects(response, reverse('users:login'))  # 確認跳轉到登入頁面
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(User.objects.filter(
            email='newuser@example.com').exists())
        self.assertTrue(User.objects.filter(
            phone_number='0912345678').exists())

    def test_username_already_exists(self):
        """
        測試使用重複 username 的情境。
        """
        User.objects.create_user(
            username='testuser', email='user1@example.com', phone_number='0911111111', password='Aa1234567890')

        response = self.client.post(reverse('users:register'), {
            'username': 'testuser',
            'email': 'user2@example.com',
            'phoneNumber': '0912345678',
            'password': 'Aa1234567890',
            'confirmPassword': 'Aa1234567890',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("該使用者名稱已被使用。", response_text)
        self.assertTemplateUsed(response, "users/register.html")

    def test_email_already_exists(self):
        """
        測試使用重複 email 的情境。
        """
        User.objects.create_user(
            username='user1', email='user1@example.com', phone_number='0911111111', password='Aa1234567890')

        response = self.client.post(reverse('users:register'), {
            'username': 'user2',
            'email': 'user1@example.com',
            'phoneNumber': '0912345678',
            'password': 'Aa1234567890',
            'confirmPassword': 'Aa1234567890',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("該電子郵件已被註冊。", response_text)
        self.assertTemplateUsed(response, "users/register.html")

    def test_phone_number_invalid(self):
        """
        測試無效手機號碼的情境。
        """
        response = self.client.post(reverse('users:register'), {
            'username': 'user3',
            'email': 'user3@example.com',
            'phoneNumber': '1234567',
            'password': 'Aa1234567890',
            'confirmPassword': 'Aa1234567890',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("請輸入有效的手機號碼（格式：09xxxxxxxx）。", response_text)
        self.assertTemplateUsed(response, "users/register.html")

    def test_password_mismatch(self):
        """
        測試密碼不一致的情境。
        """
        response = self.client.post(reverse('users:register'), {
            'username': 'user4',
            'email': 'user4@example.com',
            'phoneNumber': '0912345678',
            'password': 'Aa1234567890',
            'confirmPassword': 'Aa12345678',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("密碼與確認密碼不一致。", response_text)
        self.assertTemplateUsed(response, "users/register.html")

    def test_weak_password(self):
        """
        測試弱密碼的情境。
        """
        response = self.client.post(reverse('users:register'), {
            'username': 'user5',
            'email': 'user5@example.com',
            'phoneNumber': '0912345678',
            'password': '123456',
            'confirmPassword': '123456',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("密碼長度至少為 12 個字符。", response_text)
        self.assertTemplateUsed(response, "users/register.html")

    def test_registration_user_creation_exception(self):
        """
        測試用戶創建過程中拋出異常的情境。
        """
        with patch("users.models.User.objects.create_user") as mock_create_user:
            mock_create_user.side_effect = Exception("測試用例模擬的異常")

            response = self.client.post(reverse('users:register'), {
                'username': 'user6',
                'email': 'user6@example.com',
                'phoneNumber': '0912345678',
                'password': 'StrongPassword123!',
                'confirmPassword': 'StrongPassword123!',
            })

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "users/register.html")
            response_text = response.content.decode('utf-8')
            self.assertIn("註冊失敗，請稍後再試。", response_text)
            self.assertIn("測試用例模擬的異常", response_text)

    def test_register_get_request(self):
        """
        測試訪問註冊頁面時（GET 請求）的行為。
        """
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        response_text = response.content.decode('utf-8')
        self.assertIn('value=""', response_text)


class LoginTest(TestCase):
    def setUp(self):
        """
        初始化測試數據。
        """
        session = self.client.session
        session["security_verified"] = True
        session.save()

        # 創建測試用戶
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPassword123!",
        )

    def test_login_successful(self):
        """
        測試成功登入的情境，跳轉到顧客儀表板。
        """
        response = self.client.post(reverse('users:login'), {
            'email': self.user.email,
            'password': 'TestPassword123!',
        })
        self.assertRedirects(response, reverse(
            'users:customer_dashboard'))  # 確認跳轉到儀表板

    def test_login_invalid_email(self):
        """
        測試使用不存在的 email 登入的情境。
        """
        response = self.client.post(reverse('users:login'), {
            'email': 'nonexistent@example.com',
            'password': 'TestPassword123!',
        })
        response_text = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)  # 應停留在登入頁
        self.assertIn("信箱或密碼不正確", response_text)  # 與 views 中的統一錯誤訊息一致

    def test_login_invalid_password(self):
        """
        測試使用錯誤密碼登入的情境。
        """
        response = self.client.post(reverse('users:login'), {
            'email': self.user.email,
            'password': 'WrongPassword123!',
        })
        response_text = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)  # 應停留在登入頁
        self.assertIn("信箱或密碼不正確", response_text)  # 與 views 中的統一錯誤訊息一致

    def test_login_empty_fields(self):
        """
        測試未填寫 email 或密碼的情境。
        """
        response = self.client.post(reverse('users:login'), {
            'email': '',
            'password': '',
        })
        response_text = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)  # 應停留在登入頁
        self.assertIn("請輸入信箱和密碼", response_text)

    def test_logout(self):
        """
        測試用戶登出後是否正確跳轉並清除狀態。
        """
        # 先登入用戶
        self.client.post(reverse('users:login'), {
            'email': self.user.email,
            'password': 'TestPassword123!',
        })

        # 驗證 session 是否包含用戶
        self.assertIn('_auth_user_id', self.client.session)

        # 登出用戶
        response = self.client.get(reverse("users:logout"))

        # 驗證重定向到登入頁面
        self.assertRedirects(response, reverse("users:login"))

        # 驗證 session 中用戶 ID 被清除
        self.assertNotIn('_auth_user_id', self.client.session)
