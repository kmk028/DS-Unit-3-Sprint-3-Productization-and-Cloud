"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask,render_template, request
from openaq import OpenAQ
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
api = OpenAQ()
DB = SQLAlchemy()
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/karthikmahendra/Desktop/DS-Unit-3-Sprint-3-Productization-and-Cloud/SC/db.sqlite3'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB.init_app(APP)
records =[]

with APP.app_context():
    DB.create_all()

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)
    country = DB.Column(DB.String(2))
    city = DB.Column(DB.String(25))
    location = DB.Column(DB.Text)

    def __repr__(self):
        return f'Time: {self.datetime}, Value: {self.value},City: {self.city}, Country: {self.country},Location: {self.location}'

@APP.route('/')
def root():
    """Base view."""
    if not (Record.query.all()):
        fetch_record(api)
    records = Record.query.filter(Record.value >= 10).all()
    return render_template('base.html', records=records)

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    records = Record.query.all()
    fetch_record(api)
    return render_template('base.html', title='Home', records=records, message='Records Refreshed!')

def fetch_record(api,city='Los Angeles',parameter='pm25',location=None):
    if location is None:
        status, body = api.measurements(city=city, parameter=parameter)
    else:
        status, body = api.measurements(city=city, parameter=parameter,location=location)

    for row in body['results']:
        record = Record(city=row['city'],location=row['location'], datetime=row['date']['utc'], value=row['value'])
        records = records.append(record)
    for record in records:
        DB.session.add(record)
    DB.session.commit()
    

# def update_records(api):
#     for record in records:
#         if not DB.session.query(Record).filter(Record.datetime == record.datetime).first():
#             DB.session.add(record)
#     DB.session.commit()



