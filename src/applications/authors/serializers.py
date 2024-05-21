from rest_framework import serializers
from applications.jwt_auth.models import User
from .models import Author


class UserSerializerForAuthor(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializerForAuthor(read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'user', 'bio', 'posts']

