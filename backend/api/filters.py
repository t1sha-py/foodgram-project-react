from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    """Поиск по игредиенту"""
    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтры для сортировки рецептов"""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_list = filters.BooleanFilter(
        method='filter_is_in_shopping_list'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_list',
        )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_list(self, queryset, name, value):
        if value:
            return queryset.filter(lists__user=self.request.user)
        return queryset
