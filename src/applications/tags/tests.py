from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.jwt_auth.models import User
from .models import Tag


class TagAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед набором тестов"""
        cls.admin_user = User.objects.create_superuser(email="admin@gmail.com", password="admin123")
        cls.regular_user = User.objects.create_user(email="user@gmail.com", password="user123")
        cls.tag = Tag.objects.create(name="Test Tag")
        cls.list_url = reverse("tag-list")
        cls.detail_url = reverse("tag-detail", args=[cls.tag.id])

    def test_list_tags(self):
        """Тест получения списка тегов"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{"id": self.tag.id, "name": self.tag.name}])

    def test_retrieve_tag(self):
        """Тест получения одного тега"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"id": self.tag.id, "name": self.tag.name})

    def test_create_tag_unauthorized(self):
        """Тест создания тега без авторизации"""
        data = {"name": "New Tag"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tag_as_admin(self):
        """Тест создания тега администратором"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "New Tag"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name="New Tag").exists())

    def test_update_tag_unauthorized(self):
        """Тест обновления тега без авторизации"""
        data = {"name": "Updated Tag"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_tag_as_admin(self):
        """Тест обновления тега администратором"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "Updated Tag"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, "Updated Tag")

    def test_delete_tag_unauthorized(self):
        """Тест удаления тега без авторизации"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_tag_as_admin(self):
        """Тест удаления тега администратором"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=self.tag.id).exists())

    def test_permissions_for_regular_user(self):
        """Тест, что обычный пользователь не может создавать, обновлять или удалять теги"""
        self.client.force_authenticate(user=self.regular_user)

        # Попытка создания
        create_response = self.client.post(self.list_url, {"name": "Another Tag"}, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

        # Попытка обновления
        update_response = self.client.put(self.detail_url, {"name": "Another Name"}, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)

        # Попытка удаления
        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
