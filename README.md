# Foodgram - социальная сеть о кулинарии

# Локальная установка в Docker

- Склонируйте репозитрий на свой компьютер
- Создайте `.env` файл в директории `infra/`, в котором должны содержаться следующие переменные:
    >DB_ENGINE=django.db.backends.postgresql\
    DB_NAME= # название БД\
	POSTGRES_USER= # ваше имя пользователя\
    POSTGRES_PASSWORD= # пароль для доступа к БД\
    DB_HOST=db\
    DB_PORT=5432\
    SECRET_KEY= # Secret key для Django проекта
- Из папки `infra/` соберите образ при помощи docker-compose
`$ docker-compose up -d --build`
- Создайте миграции
`$ docker-compose exec backend python manage.py makemigrations`
- Примените миграции
`$ docker-compose exec backend python manage.py migrate`
- Соберите статику
`$ docker-compose exec backend python manage.py collectstatic --no-input`
- Загрузите ингредиенты
`sudo docker-compose exec -T backend python manage.py load_data`
- Создайте теги
`sudo docker-compose exec -T backend python manage.py load_tags`
- Для доступа к админке не забудьте создать суперюзера
`$ docker-compose exec backend python manage.py createsuperuser`