from rest_framework import serializers

from applications.jwt_auth.models import User
from applications.posts.models import Author
from .models import Post
from ..categories.models import Category
from ..comments.models import Comment
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


class CommentSerializerForPost(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'date', 'content', 'user']


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializerForPost(read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True
    )
    category_details = CategorySerializerForPost(read_only=True, source="category")
    tags = TagSerializerForPost(read_only=True, many=True)
    comments = CommentSerializerForPost(read_only=True, many=True)

    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            "date_posted": {"read_only": True},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["author"] = request.user.author_data
        return super().create(validated_data)


class PostSerializerList(serializers.ModelSerializer):
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
