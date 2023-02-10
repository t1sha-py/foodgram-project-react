from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для управления пользователями"""
    list_display = (
        'id',
        'email',
        'username',
        'full_name',
    )
    list_filter = ('email', 'username',)
    search_fields = ('username',)

    # @staticmethod
    # def full_name(obj):
    #     return f'{obj.first_name} {obj.last_name}'


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
