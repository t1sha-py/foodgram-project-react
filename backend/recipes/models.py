from django.core import validators
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент',
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов"""

    name = models.CharField(
        'Название тега',
        max_length=200,
    )
    color = models.CharField(
        'Цвет',
        max_length=7
    )
    slug = models.SlugField(
        'Адрес',
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='recipes/images/',
        null=True,
        default=None,
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        default=30,
        validators=(validators.MinValueValidator(
            1, message='Время приготовления должно быть больше 0!'
        ),),
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Модель количества ингредиентов"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингредиент',
    )
    amount = models.IntegerField(
        'Количество ингредиента',
        validators=(validators.MinValueValidator(
            1, message='Ингредиентов не может быть меньше 1!'
        ),),
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique favorite',
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique shopping cart',
            )
        ]
