from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrSuperUser
from .serializers import (CustomUserSerializer, FollowSerializer,
                          IngredientSerializer, LightRecipeSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination


class FollowViewSet(APIView):
    """APIView для добавления и удаления подписки"""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def post(self, request):
        user_id = self.kwargs.get('user_id')
        if user_id == request.user.id:
            return Response(
                {'error': 'Нельзя подписаться на себя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Follow.objects.filter(
            user=request.user,
            author_id=user_id
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого автора!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        author = get_object_or_404(User, id=user_id)
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request):
        user_id = self.kwargs.get('user_id')
        get_object_or_404(User, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого автора!'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class FollowListView(ListAPIView):
    """APIView для просмотра подписок"""

    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class TagsViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов"""

    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецептов"""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrSuperUser,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer

        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)

        return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)

        return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'error': 'Рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = LightRecipeSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Рецепта не существует!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount=Sum('amount'))
        createdate = datetime.today()
        shopping_cart = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {createdate:%d-%m-%Y}\n\n'
        )
        shopping_cart += '\n'.join(
            [
                f'- {ingredient["ingredient__name"]}'
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["amount"]}'
                for ingredient in ingredients
            ]
        )
        shopping_cart += f'\n\nFoodgram ({createdate:%Y})'
        filename = f'{user.username}_shopping_carts.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
