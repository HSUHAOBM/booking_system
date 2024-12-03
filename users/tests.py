from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

# 使用自訂的用戶模型
User = get_user_model()


class RegisterTest(TestCase):
    def setUp(self):
        """
        初始化測試環境，模擬通過安全驗證。
        """
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
            'password': 'Aa1234567890',
            'confirm-password': 'Aa1234567890',
        })
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(User.objects.filter(
            email='newuser@example.com').exists())

    def test_username_already_exists(self):
        """
        測試使用重複 username 的情境。
        """
        # 創建一個已有的用戶
        User.objects.create_user(
            username='testuser', email='user1@example.com', password='Aa1234567890')

        response = self.client.post(reverse('users:register'), {
            'username': 'testuser',
            'email': 'user2@example.com',
            'password': 'Aa1234567890',
            'confirm-password': 'Aa1234567890',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("該使用者名稱已被使用", response_text)

    def test_email_already_exists(self):
        """
        測試使用重複 email 的情境。
        """
        # 創建一個已有的用戶
        User.objects.create_user(
            username='user1', email='user1@example.com', password='Aa1234567890')

        response = self.client.post(reverse('users:register'), {
            'username': 'user2',
            'email': 'user1@example.com',
            'password': 'Aa1234567890',
            'confirm-password': 'Aa1234567890',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("該信箱已被註冊", response_text)

    def test_password_mismatch(self):
        """
        測試密碼不一致的情境。
        """
        response = self.client.post(reverse('users:register'), {
            'username': 'user3',
            'email': 'user3@example.com',
            'password': 'Aa1234567890',
            'confirm-password': 'Aa12345678',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("密碼與確認密碼不一致", response_text)

    def test_weak_password(self):
        """
        測試弱密碼的情境。
        """
        response = self.client.post(reverse('users:register'), {
            'username': 'user4',
            'email': 'user4@example.com',
            'password': '123456',
            'confirm-password': '123456',
        })

        response_text = response.content.decode('utf-8')
        self.assertIn("密碼長度至少為 12 個字符", response_text)

    def test_registration_user_creation_exception(self):
        """
        測試用戶創建過程中拋出異常的情境。
        """
        # 模擬 User.objects.create_user 拋出異常
        with patch("users.models.User.objects.create_user") as mock_create_user:
            mock_create_user.side_effect = Exception("測試用例模擬的異常")

            response = self.client.post(reverse('users:register'), {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'StrongPassword123!',
                'confirm-password': 'StrongPassword123!',
            })

            # 確認返回到註冊頁面
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "users/register.html")

            # 確認顯示錯誤訊息
            response_text = response.content.decode('utf-8')
            self.assertIn("註冊失敗，請稍後再試", response_text)
            self.assertIn("測試用例模擬的異常", response_text)

            # 確認表單保留已填寫的值
            self.assertIn('value="testuser"', response_text)
            self.assertIn('value="testuser@example.com"', response_text)

    def test_register_get_request(self):
        """
        測試訪問註冊頁面時（GET 請求）的行為。
        """
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)  # 應返回 200 狀態碼
        self.assertTemplateUsed(response, "users/register.html")  # 應使用正確模板
        response_text = response.content.decode('utf-8')
        self.assertIn('value=""', response_text)  # 檢查表單的輸入框為空


class LoginTest(TestCase):
    def setUp(self):
        """
        初始化測試數據。
        """

        session = self.client.session
        session["security_verified"] = True
        session.save()

        # 創建顧客用戶
        self.customer = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="Customer123!",
            role="customer",
        )

        # 創建商家用戶
        self.merchant = User.objects.create_user(
            username="merchant1",
            email="merchant1@example.com",
            password="Merchant123!",
            role="merchant",
        )

    def test_login_customer_redirect(self):
        """
        測試顧客登入後跳轉到顧客頁面。
        """
        response = self.client.post(reverse('users:login'), {
            'email': self.customer.email,
            'password': 'Customer123!',
        })
        self.assertRedirects(response, reverse('users:customer_dashboard'))

    def test_login_successful_merchant(self):
        """
        測試商家成功登入的情境，並跳轉到商家/後台儀表板。
        """
        response = self.client.post(reverse('users:login'), {
            'email': self.merchant.email,
            'password': 'Merchant123!',
        })
        self.assertRedirects(response, reverse('users:admin_dashboard'))

    def test_login_invalid_email(self):
        """
        測試使用不存在的 email 登入的情境。
        """
        response = self.client.post(reverse('users:login'), {
            'email': 'nonexistent@example.com',
            'password': 'Customer123!',
        })
        response_text = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)  # 應停留在登入頁
        self.assertIn("該信箱尚未註冊", response_text)

    def test_login_invalid_password(self):
        """
        測試使用錯誤密碼登入的情境。
        """
        response = self.client.post(reverse('users:login'), {
            'email': self.customer.email,
            'password': 'WrongPassword123!',
        })
        response_text = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)  # 應停留在登入頁
        self.assertIn("密碼錯誤，請重新嘗試", response_text)

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
        response = self.client.get(reverse("users:logout"))
        # 驗證重定向到登入頁面
        self.assertRedirects(response, reverse("users:login"))

        # 驗證 session 中用戶 ID 被清除
        self.assertFalse("_auth_user_id" in self.client.session)
