import django_filters
from .models import Post


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class PostFilter(django_filters.FilterSet):
    tag_ids = NumberInFilter(field_name='tags__id', lookup_expr='in')
    tag_name = django_filters.CharFilter(field_name='tags__name', lookup_expr='exact')
    category_ids = NumberInFilter(field_name='category__id', lookup_expr='in')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='exact')
    author_id = django_filters.NumberFilter(field_name='author__id', lookup_expr='exact')

    class Meta:
        model = Post
        fields = ['tags', 'category', 'author']
