# Система рассылок - Настройка окружения

## Установка

1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```
2. Отредактируйте .env файл:

```bash
nano .env  # или используйте любой текстовый редактор
````
3. Заполните обязательные поля:
```
SECRET_KEY - сгенерируйте новый ключ

DB_PASSWORD - пароль для PostgreSQL

EMAIL_HOST_USER - ваш email

EMAIL_HOST_PASSWORD - пароль приложения

Генерация SECRET_KEY
```
4. Выполните команду для генерации нового секретного ключа:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
## Настройка PostgreSQL
### Установите PostgreSQL
1. Создайте базу данных и пользователя:
```sql
CREATE DATABASE mailing_db;
CREATE USER mailing_user WITH PASSWORD 'ваш-пароль';
GRANT ALL PRIVILEGES ON DATABASE mailing_db TO mailing_user;
```
2.  Запуск приложения
```bash
# Установка зависимостей
pip install -r requirements.txt

# Миграции базы данных
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver
```
## Переменные окружения
### Обязательные:
 - SECRET_KEY - секретный ключ Django 
 - DB_* - настройки базы данных 
 - EMAIL_* - настройки почты (для рассылок)

### Опциональные:
 - DEBUG - режим отладки (по умолчанию True)
 - ALLOWED_HOSTS - разрешенные домены

### Упрощенная версия `.env.example` для быстрого старта:
```bash
# 🚀 Quick Start - Быстрый старт
DEBUG=True
SECRET_KEY=замените-этот-ключ-сгенерируйте-новый

# 🗄️ Database - База данных
DB_NAME=mailing_db
DB_USER=mailing_user
DB_PASSWORD=ваш-пароль-бд
DB_HOST=localhost
DB_PORT=5432

# 📧 Email - Почта (для рассылок)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=ваш-email@gmail.com
EMAIL_HOST_PASSWORD=пароль-приложения

# 🌐 Hosts - Домены
ALLOWED_HOSTS=localhost,127.0.0.1
```
### Скрипт для автоматической настройки
#### Создайте setup_env.py для помощи в настройке:
```python
#!/usr/bin/env python3
"""
Скрипт для настройки .env файла
"""

import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

def setup_env():
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  Файл .env уже существует!")
        response = input("Перезаписать? (y/n): ")
        if response.lower() != 'y':
            print("Отменено.")
            return
    
    # Генерация секретного ключа
    secret_key = get_random_secret_key()
    
    # Шаблон .env
    env_template = f"""DEBUG=True
SECRET_KEY={secret_key}
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=mailing_db
DB_USER=mailing_user
DB_PASSWORD=введите-пароль-бд
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=ваш-email@gmail.com
EMAIL_HOST_PASSWORD=пароль-приложения
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("✅ Файл .env создан!")
    print("📝 Не забудьте отредактировать пароли в файле .env")

if __name__ == "__main__":
    setup_env()
```
### Запустите скрипт:

```bash
python setup_env.py
```
