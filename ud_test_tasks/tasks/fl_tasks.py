import requests

# задание - открывает страницу web проекта, в результате чего запускается скрипт обновления
def update_data():
    print('task update_data is start')
    return print(requests.get('http://flask:5000/update'))