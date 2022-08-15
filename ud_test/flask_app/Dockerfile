FROM python:3.9
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /flask_app
# Скачиваем/обновляем необходимые библиотеки для проекта
COPY requirements.txt /flask_app

RUN pip install --upgrade pip -r requirements.txt
# Копируем содержимое папки, где находится Dockerfile,
# в рабочую директорию контейнера
COPY . /flask_app
# Устанавливаем порт, который будет использоваться для сервера

RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 5000
