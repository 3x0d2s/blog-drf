from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.jwt_auth.models import User


class UserAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед каждым набором тестов"""
        cls.admin_user = User.objects.create_superuser(
            email="admin@gmail.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
        )
        cls.regular_user = User.objects.create_user(
            email="user@gmail.com",
            password="user123",
            first_name="Regular",
            last_name="User",
        )
        cls.create_url = reverse("user-list")
        cls.token_url = reverse("token_obtain_pair")
        cls.token_refresh_url = reverse("token_refresh")

    def authenticate_user(self, email, password):
        """Получает токен для пользователя и настраивает аутентификацию клиента"""
        response = self.client.post(self.token_url, {"email": email, "password": password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_refresh_token(self):
        """Тест обновления токена через endpoint refresh"""
        # Получаем токен для пользователя
        response = self.client.post(self.token_url, {"email": "user@gmail.com", "password": "user123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data["refresh"]

        # Используем refresh токен для получения нового access токена
        response = self.client.post(self.token_refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIsInstance(response.data["access"], str)

    def test_create_user(self):
        """Тест создания нового пользователя"""
        data = {
            "email": "newuser@gmail.com",
            "password": "newuser123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@gmail.com").exists())

    def test_create_user_already_authenticated(self):
        """Тест, что аутентифицированный пользователь не может зарегистрироваться снова"""
        self.authenticate_user(email="user@gmail.com", password="user123")
        data = {
            "email": "newuser@gmail.com",
            "password": "newuser123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_me(self):
        """Тест получения данных текущего пользователя"""
        self.authenticate_user(email="user@gmail.com", password="user123")
        response = self.client.get(reverse("user-get-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], "user@gmail.com")

    def test_get_user_details(self):
        """Тест получения данных другого пользователя"""
        self.authenticate_user(email="admin@gmail.com", password="admin123")
        url = reverse("user-detail", args=[self.regular_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@gmail.com")

    def test_update_user(self):
        """Тест обновления данных пользователя"""
        self.authenticate_user(email="user@gmail.com", password="user123")
        url = reverse("user-detail", args=[self.regular_user.id])
        data = {"first_name": "Updated"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, "Updated")

    def test_update_user_not_owner(self):
        """Тест, что пользователь не может обновлять данные другого пользователя"""
        self.authenticate_user(email="user@gmail.com", password="user123")
        url = reverse("user-detail", args=[self.admin_user.id])
        data = {"first_name": "Malicious Update"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user(self):
        """Тест удаления своего аккаунта"""
        self.authenticate_user(email="user@gmail.com", password="user123")
        url = reverse("user-detail", args=[self.regular_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())

    def test_delete_user_not_owner(self):
        """Тест, что пользователь не может удалить чужой аккаунт"""
        self.authenticate_user(email="user@gmail.com", password="user123")
        url = reverse("user-detail", args=[self.admin_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_manage_users(self):
        """Тест, что администратор может редактировать и удалять пользователей"""
        self.authenticate_user(email="admin@gmail.com", password="admin123")

        # Обновление пользователя
        update_url = reverse("user-detail", args=[self.regular_user.id])
        update_data = {"first_name": "Admin Updated"}
        update_response = self.client.patch(update_url, update_data, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, "Admin Updated")

        # Удаление пользователя
        delete_response = self.client.delete(update_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())
