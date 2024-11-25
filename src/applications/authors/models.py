from django.db import models
from applications.jwt_auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_data')
    bio = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.user.get_full_name()}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.author_data.save()
