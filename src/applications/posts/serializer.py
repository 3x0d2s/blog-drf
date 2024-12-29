from .models import Post
from rest_framework import serializers
from applications.jwt_auth.models import User
from applications.posts.models import Author
from ..categories.models import Category
from ..tags.models import Tag


class UserSerializerForAuthorForPost(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class AuthorSerializerForPost(serializers.HyperlinkedModelSerializer):
    user = UserSerializerForAuthorForPost(read_only=True)

    class Meta:
        model = Author
        fields = ['url', 'id', 'user', 'bio']


class CategorySerializerForPost(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Category
        fields = ['url', 'id', 'name']


class TagSerializerForPost(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializerForPost(read_only=True)
    category = CategorySerializerForPost(read_only=True)
    tags = TagSerializerForPost(read_only=True, many=True)

    class Meta:
        model = Post
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["author"] = request.user.author_data
        return super().create(validated_data)
