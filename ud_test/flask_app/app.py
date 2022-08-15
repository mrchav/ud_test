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

source_spreadsheet_id = '1K-VI_iqMvKMHpF9TxmyFGutZj6nYjrwARuxbk98lF6s'
target_spreadsheet_id = '1vra9RoSK2vJ0SEfVVYJwGjxoHVeJ5M_b--TbOE0QGFU'

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
)



@app.route('/update')
def udate_page():
    get_usa_rate()
    orders_in_source = get_google_sheet_data()['values'][1:]

    orders_in_base = Order.query.update({'active': False})

    for r in orders_in_source:
        new_order = Order(r[0], r[1], r[2], datetime.strptime(r[3], '%d.%m.%Y'))
        print(f'source id {r[0]} order number{r[1]} cost us {r[2]} date {r[3]}')
        db.session.add(new_order)
        db.session.flush()

    db.session.commit()


    return 'hi'

@app.route('/')
def main_page():
    orders_in_base = Order.query.filter(Order.active == True).all()

    return render_template('main_page.html', title='Все операции', orders=orders_in_base)


def get_google_sheet_data():

    httpAuth = credentials.authorize(httplib2.Http())
    service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)

    values = service.spreadsheets().values().get(
        spreadsheetId=source_spreadsheet_id,
        range='Sheet',
        majorDimension='ROWS'
    ).execute()

    #push_google_sheet_data(values['values'])
    return values

def get_usa_rate():

    rn = ET.fromstring(requests.get("http://www.cbr.ru/scripts/XML_daily.asp").text)
    for child in rn:
        if child.get('ID') == 'R01235':
            #print(f"курс доллара {child.find('Value').text}")
            usa_dol_rate = child.find('Value').text
    return float(usa_dol_rate.replace(",","."))


class Order(db.Model):

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Integer, nullable=True)
    source_id = db.Column(db.Integer, nullable=True)
    cost_us = db.Column(db.Integer)
    cost_ru = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

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