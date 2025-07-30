# Foodgram

**Foodgram** — платформа для публикации и поиска рецептов, составления списка покупок и подписки на любимых авторов.

[![foodgram](https://img.shields.io/badge/Deployed_on-bestfoodgram.sytes.net-blue)](https://bestfoodgram.sytes.net)

---

## Оглавление

- [Описание](#описание)
- [Технологии](#технологии)
- [Запуск проекта](#запуск-проекта)
- [CI/CD](#cicd)
- [Контакты](#контакты)

---

## Описание

**Foodgram** — это проект, где:

- можно публиковать свои рецепты;
- искать рецепты по ингредиентам и тегам;
- добавлять понравившиеся рецепты в избранное;
- формировать список покупок;
- подписываться на других пользователей.

---

## Технологии

- Python 3.9+
- Django, Django REST Framework, Djoser
- PostgreSQL
- Docker, Docker Compose
- Nginx, Gunicorn
- GitHub Actions (CI/CD)
- React (frontend, отдельный контейнер)

---

## Запуск проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/Vladimir-Samoilov/foodgram.git
cd foodgram
```

### 2. Переменные окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password
DB_HOST=db
DB_PORT=5432

DEBUG=False
ALLOWED_HOSTS=bestfoodgram.sytes.net,127.0.0.1,localhost,backend
SECRET_KEY=your_secret_key
```

### 3. Запуск в Docker

Для локального запуска:

```bash
sudo docker compose -f docker-compose.yml up --build -d
```

Для продакшн (пример):

```bash
sudo docker compose -f docker-compose.production.yml up -d
```

### 4. Загрузка фикстур

Фикстуры (например, ингредиенты) находятся в папке `/data` или `/app/data` внутри контейнера:

```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata /app/data/ingredients_fixture.json
```

### 5. Создание суперпользователя

```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

---

## CI/CD

Для автоматизации используется GitHub Actions:

- Проверка стиля и тестов
- Сборка и пуш Docker-образов
- Автоматический деплой на сервер через ssh

Пример workflow-файла: `.github/workflows/main.yml`

---

## Контакты

Автор: Владимир Самойлов

Проект развёрнут: <https://bestfoodgram.sytes.net>