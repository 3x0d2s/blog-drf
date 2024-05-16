from django.db import models
from applications.authors.models import Author
from applications.categories.models import Category
from applications.tags.models import Tag


class Post(models.Model):
    header = models.CharField(max_length=200)
    body = models.CharField(max_length=10000)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts")
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
