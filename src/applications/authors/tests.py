from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.jwt_auth.models import User
from .models import Author


class AuthorAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед набором тестов"""
        cls.admin_user = User.objects.create_superuser(email="admin@gmail.com", password="admin123", first_name="Admin", last_name="User")
        cls.regular_user = User.objects.create_user(email="user@gmail.com", password="user123", first_name="Regular", last_name="User")
        cls.author = Author.objects.get(user=cls.regular_user)  # Автор создается автоматически сигналом
        cls.list_url = reverse("author-list")
        cls.detail_url = reverse("author-detail", args=[cls.author.id])

    def test_list_authors(self):
        """Тест получения списка авторов"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": self.author.id,
                    "user": {
                        "id": self.regular_user.id,
                        "email": self.regular_user.email,
                        "first_name": self.regular_user.first_name,
                        "last_name": self.regular_user.last_name,
                    },
                    "bio": self.author.bio,
                    "posts": [],
                }
            ]
        )

    def test_retrieve_author(self):
        """Тест получения одного автора"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": self.author.id,
                "user": {
                    "id": self.regular_user.id,
                    "email": self.regular_user.email,
                    "first_name": self.regular_user.first_name,
                    "last_name": self.regular_user.last_name,
                },
                "bio": self.author.bio,
                "posts": [],
            }
        )

    def test_list_authors_excludes_admin(self):
        """Тест, что список авторов не содержит администратора"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors_ids = [author["id"] for author in response.json()]
        self.assertNotIn(self.admin_user.id, authors_ids)

    def test_author_creation_on_user_creation(self):
        """Тест, что автор создается автоматически при создании пользователя"""
        new_user = User.objects.create_user(email="newuser@gmail.com", password="newuser123", first_name="New", last_name="User")
        author = Author.objects.get(user=new_user)
        self.assertIsNotNone(author)
        self.assertEqual(author.user, new_user)

    def test_author_update_signal(self):
        """Тест, что данные автора обновляются при обновлении пользователя"""
        self.regular_user.first_name = "Updated"
        self.regular_user.save()
        self.author.refresh_from_db()
        self.assertEqual(self.author.user.first_name, "Updated")

    def test_non_existing_author_retrieve(self):
        """Тест получения несуществующего автора"""
        invalid_detail_url = reverse("author-detail", args=[999])
        response = self.client.get(invalid_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
