from datetime import datetime
import xml.etree.ElementTree as ET

import requests
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from flask_migrate import Migrate

import httplib2
import googleapiclient.discovery

from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123123@db:5432/test_ud"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#путь к фаилу с доступом к google sheets
CREDENTIALS_FILE = 'credentials.json'

# фаил google sheets - источник данных.
# #https://docs.google.com/spreadsheets/d/1K-VI_iqMvKMHpF9TxmyFGutZj6nYjrwARuxbk98lF6s/edit#gid=0
source_spreadsheet_id = '1K-VI_iqMvKMHpF9TxmyFGutZj6nYjrwARuxbk98lF6s'

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
)


# URL при переходе по которому обновляются данные в таблице.
# Данный URL периодически открывается в задачах, для обновления данных.
# Надо переписать его через API
@app.route('/update')
def udate_page():
    # Обновляем курс доллога.
    get_usa_rate()
    # Получаем данные с гугл таблицы. И оставляем все, кроме 1 строчки
    orders_in_source = get_google_sheet_data()['values'][1:]
    # Вместо удаление старых данных, обновляем у них статус на неактивные.
    orders_in_base = Order.query.update({'active': False})
    # Перебираем полученные данные с таблицы и создаем новый объек класса Order на основе полученных данных
    for r in orders_in_source:
        new_order = Order(r[0], r[1], r[2], datetime.strptime(r[3], '%d.%m.%Y'))
        print(f'source id {r[0]} order number{r[1]} cost us {r[2]} date {r[3]}')
        db.session.add(new_order)
        db.session.flush()

    #загружаем новые объекты в БД
    db.session.commit()
    return 'hi'

# Главная старица сайта, на которой получаем информацию о всех текущих заказах
@app.route('/')
def main_page():
    # Достаем из базы все активные заказы. При необходимости можно ввести сортировку
    orders_in_base = Order.query.filter(Order.active == True).all()
    # Рендерим страницу и передаем в нее все полученные объекты
    return render_template('main_page.html', title='Все операции', orders=orders_in_base)

# Парсим данные с Google таблицы
def get_google_sheet_data():

    httpAuth = credentials.authorize(httplib2.Http())
    service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)

    values = service.spreadsheets().values().get(   #запрос к API google
        spreadsheetId=source_spreadsheet_id,        #фаил к которому обращаемся
    range='Sheet',                                  #Область, которую забираем - в нашем случае лист
        majorDimension='ROWS'                       #Порядок расположения данных, в нашем случае как в оригинале - строки
    ).execute()

    return values

# Обновляем курс доллора
def get_usa_rate():
    # запрос к XML ЦБ. Данные за текущее число
    rn = ET.fromstring(requests.get("http://www.cbr.ru/scripts/XML_daily.asp").text)
    #перебираем всех "детей", пока не встретим ID интересующей нас валюты
    for child in rn:
        if child.get('ID') == 'R01235':
            #Забираем курс доллора, меняя на нужный нам формат
            usa_dol_rate = child.find('Value').text
    return float(usa_dol_rate.replace(",","."))

# Создаем модель заказа
class Order(db.Model):
    # Название таблицы в БД данной модели
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)            # ID в базе
    order_number = db.Column(db.Integer, nullable=True)     # Номер заказа
    source_id = db.Column(db.Integer, nullable=True)        # ID в исходной таблице
    cost_us = db.Column(db.Integer)                         # Стоимость в уе
    cost_ru = db.Column(db.Integer)                         # Стоимость в рубля
    date = db.Column(db.DateTime)                           # Дата поставки
    update_date = db.Column(db.DateTime)                    # Дата обновления информации о заказе
    active = db.Column(db.Boolean)                          # Активен ли заказ или нет

    #
    #Конструктор нового обхекта
    #
    def __init__(self, source_id, order_number, cost_us, date):
        self.source_id = source_id
        self.order_number = order_number
        self.cost_us = cost_us
        self.cost_ru = int(int(cost_us) * actual_rate)
        self.date = date
        self.update_date = datetime.now()
        self.active = True
    def __repr__(self):
        return f"<Order number {self.order_number}>"

if __name__ == '__main__':
    actual_rate = get_usa_rate()
    app.run(host="0.0.0.0", debug=True)