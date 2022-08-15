import requests

def update_data():
    print('task update_data is start')
    return print(requests.get('http://flask:5000/update'))