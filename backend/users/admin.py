from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для управления пользователями"""
    list_display = (
        'id',
        'email',
        'username',
    )
    list_filter = ('email', 'username',)
    search_fields = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
    )
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = '-пусто-'
