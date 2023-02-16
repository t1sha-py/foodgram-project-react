from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя"""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели пользователя"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False

        return Follow.objects.filter(user=user, author=obj.id).exists()


class LightRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенного описания рецепта"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(CustomUserSerializer):
    """Сериализатор получения подписок"""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        return LightRecipeSerializer(recipes, many=True).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиентов"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецепатов"""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_ingredients(self, obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)

        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False

        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов"""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта"""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = AddIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def valiate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Нужно выбрать игредиенты!'}
            )
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredient_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты должны быть уникальными!'}
                )
            ingredient_list.append(ingredient_id)
            amount = ingredient['amount']
            if amount < 1:
                raise serializers.ValidationError(
                    {'amount': 'Ингредиентов не может быть меньше 1!'}
                )

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Необходимо выбрать хотябы один тег!'}
            )
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    {'tags': 'Теги должны быть уникальными!'}
                )
            tags_list.append(tag)

        cooking_time = data['cooking_time']
        if cooking_time <= 0:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления должно быть больше 0!'}
            )

        return data

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags')
            )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}

        return RecipeListSerializer(instance, context=context).data
