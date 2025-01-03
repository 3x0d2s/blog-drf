from django.db import models

from applications.jwt_auth.models import User
from applications.posts.models import Post


class Comment(models.Model):
    content = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
