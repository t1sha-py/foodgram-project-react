from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер создания кастомного пользователя"""
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Поле email должно быть заполнено')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь доллжен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь доллжен иметь is_superuser=True.'
            )

        return self.create_user(email, password, **extra_fields)
