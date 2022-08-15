FROM python:3.9
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /flask_app
# Скачиваем/обновляем необходимые библиотеки для проекта
COPY requirements.txt /flask_app

RUN pip install --upgrade pip -r requirements.txt
# Копируем содержимое папки, где находится Dockerfile,
# в рабочую директорию контейнера
COPY . /flask_app

# Добавляем "точку входа" по которой у нас обновляется структура БД и запускается приложение
RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

# Устанавливаем порт, который будет использоваться для сервера
EXPOSE 5000
