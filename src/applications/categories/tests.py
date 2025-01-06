from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.jwt_auth.models import User
from .models import Category


class CategoryAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед набором тестов"""
        cls.admin_user = User.objects.create_superuser(email="admin@gmail.com", password="admin123")
        cls.regular_user = User.objects.create_user(email="user@gmail.com", password="user123")
        cls.category = Category.objects.create(name="Test Category")
        cls.list_url = reverse("category-list")
        cls.detail_url = reverse("category-detail", args=[cls.category.id])

    def test_list_categories(self):
        """Тест получения списка категорий"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{"id": self.category.id, "name": self.category.name}])

    def test_retrieve_category(self):
        """Тест получения одной категории"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"id": self.category.id, "name": self.category.name})

    def test_create_category_unauthorized(self):
        """Тест создания категории без авторизации"""
        data = {"name": "New Category"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_as_admin(self):
        """Тест создания категории администратором"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "New Category"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="New Category").exists())

    def test_update_category_unauthorized(self):
        """Тест обновления категории без авторизации"""
        data = {"name": "Updated Category"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_category_as_admin(self):
        """Тест обновления категории администратором"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "Updated Category"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")

    def test_delete_category_unauthorized(self):
        """Тест удаления категории без авторизации"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category_as_admin(self):
        """Тест удаления категории администратором"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_permissions_for_regular_user(self):
        """Тест, что обычный пользователь не может создавать, обновлять или удалять категории"""
        self.client.force_authenticate(user=self.regular_user)

        # Попытка создания
        create_response = self.client.post(self.list_url, {"name": "Another Category"}, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

        # Попытка обновления
        update_response = self.client.put(self.detail_url, {"name": "Another Name"}, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)

        # Попытка удаления
        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
