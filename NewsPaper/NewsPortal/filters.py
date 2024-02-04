import django_filters
from django.forms import DateInput
from django_filters import FilterSet
from .models import Post


class PostFilter(FilterSet):

    title = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    author__user__username = django_filters.CharFilter(lookup_expr='icontains', label='Автор')
    creation_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}), lookup_expr='gte')
    class Meta:

        model = Post
        fields = ['title', 'author__user__username', 'creation_date']
