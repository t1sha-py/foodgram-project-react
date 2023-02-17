# Foodgram - Продуктовый помощник

## Описание проекта

В этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Сервис доступен по адресу http://pythonok.ru/

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
- Для доступа к админке не забудьте создать суперюзера!
`$ docker-compose exec backend python manage.py createsuperuser`

Superuser: admin@test.com

Pass: Qq123123!

## Авторы:
- [Максим Тихонов](https://github.com/t1sha-py) Бэкенд и деплой.
- [Яндекс.Практикум](https://github.com/yandex-praktikum) Фронтенд.

![workflow](https://github.com/t1sha-py/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)