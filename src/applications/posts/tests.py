from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.authors.models import Author
from applications.categories.models import Category
from applications.jwt_auth.models import User
from applications.tags.models import Tag
from .models import Post


class PostAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед каждым тестом"""
        cls.admin_user = User.objects.create_superuser(email="admin@gmail.com", password="admin123")
        cls.regular_user = User.objects.create_user(email="user@gmail.com", password="user123")
        cls.other_user = User.objects.create_user(email="otheruser@gmail.com", password="other123")

        cls.author = Author.objects.get(user=cls.regular_user)
        cls.author.bio = "Regular user bio"
        cls.author.save()
        cls.other_author = Author.objects.get(user=cls.other_user)
        cls.other_author.bio = "Other user bio"
        cls.other_author.save()

        cls.category = Category.objects.create(name="Test Category")
        cls.tag1 = Tag.objects.create(name="Tag1")
        cls.tag2 = Tag.objects.create(name="Tag2")

        cls.post = Post.objects.create(
            header="Test Post",
            body="This is a test post body",
            author=cls.author,
            category=cls.category,
        )
        cls.post.tags.add(cls.tag1, cls.tag2)

        cls.list_url = reverse("post-list")
        cls.detail_url = reverse("post-detail", args=[cls.post.id])

    def test_list_posts(self):
        """Тест получения списка постов"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["header"], self.post.header)

    def test_retrieve_post(self):
        """Тест получения одного поста"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["header"], self.post.header)

    def test_create_post_as_authenticated_user(self):
        """Тест создания поста авторизованным пользователем"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "header": "New Post",
            "body": "This is a new post",
            "category": self.category.id,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(header="New Post").exists())

    # def test_create_post_with_toxicity_check(self):
    #     """Тест токсичности текста при создании поста"""
    #     self.client.force_authenticate(user=self.regular_user)
    #     data = {
    #         "header": "Toxic Header",
    #         "body": "Toxic Body",  # Предположим, что эта комбинация будет признана токсичной
    #         "category": self.category.id,
    #     }
    #     with override_settings(TOXICITY_THRESHOLD=1):
    #         response = self.client.post(self.list_url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("ToxicityError", response.data)

    def test_update_post_as_owner(self):
        """Тест обновления поста владельцем"""
        self.client.force_authenticate(user=self.regular_user)
        data = {"header": "Updated Header"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.header, "Updated Header")

    def test_update_post_as_non_owner(self):
        """Тест обновления поста не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        data = {"header": "Malicious Update"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_as_owner(self):
        """Тест удаления поста владельцем"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_as_non_owner(self):
        """Тест удаления поста не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_posts_by_tag(self):
        """Тест фильтрации постов по тегу"""
        response = self.client.get(f"{self.list_url}?tag_ids={self.tag1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_search_posts(self):
        """Тест поиска постов по заголовку и тексту"""
        response = self.client.get(f"{self.list_url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_ordering_posts(self):
        """Тест сортировки постов"""
        Post.objects.create(
            header="Older Post",
            body="Older body",
            author=self.author,
            category=self.category,
        )
        response = self.client.get(f"{self.list_url}?ordering=-date_posted")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]["header"], "Older Post")
