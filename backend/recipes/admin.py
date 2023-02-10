from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingList, Tag)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для управления избранным"""
    list_display = (
        'id',
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для управления ингредиентами"""
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    """Админка для управления количеством ингредиентов"""
    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount',
    )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для управления рецептами"""
    list_display = (
        'id',
        'name',
        'author',
        'amount_favorites',
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    empty_value_display = '-пусто-'

    @staticmethod
    def amount_favorites(obj):
        return obj.favorites.count()


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Админка для управления списком покупок"""
    list_display = (
        'id',
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для управления тегами"""
    list_display = (
        'id',
        'name',
        'slug',
    )
    empty_value_display = '-пусто-'
