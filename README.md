#  Foodgram

https://foodzueva.ddns.net/recipes

## Описание проекта

Проект «Фудграм» — сайт, на котором пользователи публикуют рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Это полностью рабочий проект, который состоит из бэкенд-приложения на Django и фронтенд-приложения на React.

[![Workflow Status](https://github.com/dariazueva/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/dariazueva/foodgram-project-react/actions/workflows/main.yml)


### Основной функционал проекта:

- Регистрация новых пользователей
- Вход и выход зарегистрированных пользователей
- Просмотр рецептов с их фотками
- Создание, редактирование и удаление рецептов
- Добавление и изменение списка избранного и покупок

### Основной стек технологий проекта:

django, gunicorn, nginx, docker, react, github actions, node.js, postgresql, django rest 

### Как запустить проект на удаленном сервере с помощью Docker:

#### Создайте директорию foodgram .
```bash
mkdir foodgram
cd foodgram
```
#### Скачайте или скопируйте файл docker-compose.production.yml из этого репозитория.

#### Создайте файл .env и заполните его своими данными по образцу.
```bash
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY = ваш-секретный-ключ
ALLOWED_HOSTS = localhost,127.0.0.1,backend,ваш-домен
```
#### Запустите систему контейнеров.
```bash
sudo docker compose -f docker-compose.production.yml up
```
#### Выпоните миграции в контейнере backend.
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
#### Загрузите фикструы ингредиентов и тегов.
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_fixture
```
#### Соберите статику.
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
#### Копируйте собранную статику.
```bash
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
#### Создайте суперпользователя.
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Где посмотреть документацию:
С ней можно ознакомиться по адресу https://foodzueva.ddns.net/api/docs/.

## Автор
Зуева Дарья Дмитриевна
Github https://github.com/dariazueva/
