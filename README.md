# Foodgram
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

django, gunicorn, nginx, docker, react, github actions, node.js, postgresql, djando rest 

### Как развернуть проект:

#### Клонируйте репозиторий.
```bash
git clone git@github.com:dariazueva/foodgram-project-react.git
```
#### Перейдите в директорию бэкенд-приложения проекта.
```bash
cd foodgram-project-react/backend/
```
#### Создайте виртуальное окружение.
```bash
python3 -m venv venv
```
#### Активируйте виртуальное окружение.
```bash
source venv/bin/activate
```
#### Установите зависимости.
```bash
pip install -r requirements.txt
```
#### Создайте файл .env и заполните его своими данными по образцу.
```bash
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```
#### Логин и пароль администратора для проверки админки:
Логин: D
Пароль: eee31415

## Автор
Зуева Дарья Дмитриевна
Github https://github.com/dariazueva/
