# Dockerfile

# Используем официальный образ Python как базовый
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта в контейнер
COPY . /app/

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска приложения (может быть изменена в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]