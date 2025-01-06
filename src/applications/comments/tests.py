from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.authors.models import Author
from applications.categories.models import Category
from applications.jwt_auth.models import User
from applications.posts.models import Post
from applications.tags.models import Tag
from .models import Comment


class CommentAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед каждым набором тестов"""
        cls.admin_user = User.objects.create_superuser(email="admin@gmail.com", password="admin123")
        cls.regular_user_1 = User.objects.create_user(email="user1@gmail.com", password="user123")
        cls.regular_user_2 = User.objects.create_user(email="user2@gmail.com", password="user123")

        cls.author = Author.objects.get(user=cls.regular_user_1)
        cls.author.bio = "Test Bio"
        cls.author.save()
        cls.category = Category.objects.create(name="Test Category")
        cls.tag = Tag.objects.create(name="Test Tag")

        cls.post = Post.objects.create(
            header="Test Post",
            body="Post content",
            author=cls.author,
            category=cls.category,
        )
        cls.post.tags.add(cls.tag)

        cls.comment = Comment.objects.create(
            content="Test Comment",
            post=cls.post,
            user=cls.regular_user_1
        )

        cls.list_url = reverse("comment-list")
        cls.detail_url = reverse("comment-detail", args=[cls.comment.id])

    def test_list_comments(self):
        """Тест получения списка комментариев"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Преобразование 'Z' в '+00:00' для сравнения
        result = response.json()
        result[0]["date"] = result[0]["date"].replace("Z", "+00:00")
        self.assertEqual(
            result,
            [
                {
                    "id": self.comment.id,
                    "content": self.comment.content,
                    "date": self.comment.date.isoformat(),
                    "post": self.comment.post.id,
                    "user": self.comment.user.id,
                }
            ]
        )

    def test_retrieve_comment(self):
        """Тест получения одного комментария"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Преобразование 'Z' в '+00:00' для сравнения
        result = response.json()
        result["date"] = result["date"].replace("Z", "+00:00")
        self.assertEqual(
            result,
            {
                "id": self.comment.id,
                "content": self.comment.content,
                "date": self.comment.date.isoformat(),
                "post": self.comment.post.id,
                "user": self.comment.user.id,
            }
        )

    def test_create_comment_unauthorized(self):
        """Тест создания комментария без авторизации"""
        data = {"content": "New Comment", "post": self.post.id}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_as_authenticated_user(self):
        """Тест создания комментария авторизованным пользователем"""
        self.client.force_authenticate(user=self.regular_user_1)
        data = {"content": "New Comment", "post": self.post.id}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(content="New Comment", post=self.post, user=self.regular_user_1).exists())

    def test_update_comment_as_owner(self):
        """Тест обновления комментария владельцем"""
        self.client.force_authenticate(user=self.regular_user_1)
        data = {"content": "Updated Comment"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Updated Comment")

    def test_update_comment_as_non_owner(self):
        """Тест обновления комментария не владельцем"""
        self.client.force_authenticate(user=self.regular_user_2)
        data = {"content": "Malicious Update"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_as_owner(self):
        """Тест удаления комментария владельцем"""
        self.client.force_authenticate(user=self.regular_user_1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_as_non_owner(self):
        """Тест удаления комментария не владельцем"""
        self.client.force_authenticate(user=self.regular_user_2)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_for_admin_user(self):
        """Тест, что администратор может удалять и изменять комментарии"""
        self.client.force_authenticate(user=self.admin_user)

        # Проверка обновления
        update_data = {"body": "Admin Updated Comment"}
        update_response = self.client.patch(self.detail_url, update_data, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Проверка удаления
        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
