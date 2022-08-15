FROM python:3.9
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /tasks
# Скачиваем/обновляем необходимые библиотеки для проекта
COPY requirements.txt /tasks

RUN pip install --upgrade pip -r requirements.txt
# Копируем содержимое папки, где находится Dockerfile,
# в рабочую директорию контейнера
COPY . /tasks

RUN chmod u+x ./entrypoint_first.sh
RUN chmod u+x ./entrypoint_second.sh
RUN chmod u+x ./entrypoint_tasks_script.sh

#ENTRYPOINT ["./entrypoint_first.sh"]
#CMD [""]
