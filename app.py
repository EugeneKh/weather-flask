import sys

import requests
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from myid.appid import appid
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'some_secret'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


db.create_all()


def not_exist(city_name):
    with open('/home/eugene/PycharmProjects/Weather App/Weather App/task/web/city.txt') as f:
        for city in f.readlines():
            if city_name.lower() == city.lower().rstrip():
                return False
    return True


def in_base(city_name):
    city = city_name.lower()
    resp = City.query.filter_by(name=city).first()
    return bool(resp)


def get_weather(all_city):
    all_weather = []
    for city in all_city:
        params = dict(
            q=city.name,
            appid=appid,
            units='metric',
        )
        r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
        w = r.json()
        w['base_id'] = city.id
        all_weather.append(w)
    return all_weather


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        city_name = request.form['city_name']

        if not_exist(city_name):
            flash("The city doesn't exist!")
            return redirect(url_for('index'))

        if in_base(city_name):
            flash("The city has already been added to the list!")
            return redirect(url_for('index'))

        city = City(name=city_name.lower())
        db.session.add(city)
        db.session.commit()
        return redirect(url_for('index'))

    all_city = City.query.all()
    all_weather = get_weather(all_city)
    return render_template('index.html', all_weather=all_weather)


@app.route('/delete/<base_id>', methods=['GET', 'POST'])
def delete(base_id):
    city = City.query.filter_by(id=base_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index'))


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
