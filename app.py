from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client as TwilioClient

from sqlalchemy import and_
import os
import requests
import json

from utils import Coordinate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite://///Users/eric/GITHUB/codevscovid19/volunteers.db"
app.config["SQLALCHEMY_BINDS"] = {
    "clients": "sqlite://///Users/eric/GITHUB/codevscovid19/clients.db"
}

# app.config.from_object(os.environ['APP_SETTINGS'])
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from volunteer import Volunteer
from client import Client

db.create_all()

locationiq_url = "https://us1.locationiq.com/v1/search.php"
sandbox_number = "+14155238886"
sandbox_code = "join lower-parent"


# twilio service
account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_TOKEN')
if account_sid is None:
    raise ValueError("Missing TWILIO_SID")
if auth_token is None:
    raise ValueError("Missing TWILIO_TOKEN")
client = TwilioClient(account_sid, auth_token)


@app.route("/get_volunteers")
def get_volunteers():
    """
    Example:

    https://3fb61cb3.ngrok.io/get_volunteers?pwd=PASSWORD&city=Lausanne

    https://3fb61cb3.ngrok.io/get_volunteers?pwd=PASSWORD&lon=6.58989274833333&lat=46.5267366&dist=5

    where PASSWORD should be replaced with appropriate password
    """

    pwd = request.args.get('pwd')
    if pwd != os.environ.get('COVID19_TOKEN'):
        return "Access denied"

    city = request.args.get('city')
    longitude = request.args.get('lon')
    if longitude is not None:
        longitude = float(longitude)
    latitude = request.args.get('lat')
    if latitude is not None:
        latitude = float(latitude)
    max_dist = request.args.get('dist')
    if max_dist is None:
        max_dist = 5
    else:
        max_dist = float(max_dist)

    # query registered volunteers
    # reg_volunteer = Volunteer.query.filter(Volunteer.latitude.isnot(None))
    if longitude is not None and latitude is not None:

        coord = Coordinate(lon=longitude, lat=latitude)
        max_coord, min_coord = coord.bounding_box(max_dist=max_dist)
        reg_volunteer = Volunteer.query.filter(
            and_(
                Volunteer.longitude.between(min_coord.lon, max_coord.lon),
                Volunteer.latitude.between(min_coord.lat, max_coord.lat)
            )
        )
    elif city is not None:
        reg_volunteer = Volunteer.query.filter_by(city=city)
    else:
        raise ValueError("Provide GPS coordinates or city.")

    # build result
    n_volunteers = reg_volunteer.count()
    result = {
            "n_volunteers": n_volunteers
        }

    numbers = reg_volunteer.all()
    volunteers = []
    for _num in numbers:
        volunteers.append(_num.serialize())
    result["volunteers"] = volunteers
    return result


@app.route("/delete", methods=['GET', 'POST'])
def remove():
    """
    Example:

    https://3fb61cb3.ngrok.io/delete
    """

    if request.method == "POST":
        number = request.form.get('number').replace(" ", "")  # remove spaces
        reg_volunteer = Volunteer.query.filter_by(number=number).first()
        reg_client = Client.query.filter_by(number=number).first()

        if reg_volunteer is not None or reg_client is not None:
            if reg_volunteer is not None:
                db.session.delete(reg_volunteer)
                db.session.commit()
            if reg_client is not None:
                db.session.delete(reg_client)
                db.session.commit()
            return redirect(url_for('removed', number=number))
        else:
            return redirect(url_for('not_in_database', number=number))

    return render_template("delete.html")


@app.route('/removed')
def removed():
    number = request.args.get('number')
    return render_template(
        'removed.html',
        number=number
    )


@app.route('/not_in_database')
def not_in_database():
    number = request.args.get('number')
    return render_template(
        'not_in_database.html',
        number=number
    )


@app.route("/get_info", methods=['GET', 'POST'])
def get_info():
    """
    Example:

    https://3fb61cb3.ngrok.io/get_info
    """

    if request.method == "POST":
        number = request.form.get('number').replace(" ", "")  # remove spaces
        reg_volunteer = Volunteer.query.filter_by(number=number)

        if reg_volunteer.count() == 0:
            return redirect(url_for('not_in_database', number=number))
        else:
            info = reg_volunteer.first().serialize()
            body = [
                f"*{_key}* : {info[_key]}" for _key in info.keys()
            ]
            body = "\n".join(body)
            body = "Hey there! This is the info we have on you:\n\n" + body
            client.messages.create(
                from_=f'whatsapp:{sandbox_number}',
                body=body,
                to='whatsapp:{}'.format(number)
            )
            return redirect(url_for('sent_info', number=number))
            # return f"sent message : {message.sid}"

    return render_template("get_info.html")


@app.route('/sent_info')
def sent_info():
    number = request.args.get('number')
    return render_template(
        'sent_info.html',
        number=number,
        sandbox_number=sandbox_number,
        sandbox_code=sandbox_code
    )


@app.route("/", methods=['GET', 'POST'])
def add_volunteer_form():
    """
    Example:

    https://3fb61cb3.ngrok.io/volunteer
    """

    if request.method == "POST":
        number = request.form.get('number').replace(" ", "")   # remove spaces
        street = request.form.get('street')
        city = request.form.get('city')
        country = request.form.get('country')
        is_available_morning = request.form.get('morning') != None
        is_available_afternoon = request.form.get('afternoon') != None
        is_available_evening = request.form.get('evening') != None

        if street == "":
            street = None
        if city == "":
            city = None
        if country == "":
            country = None
        if street is not None and city is not None and country is not None:
            # geolocate
            data = {
                'key': os.environ.get('LOCATIONIQ_TOKEN'),
                'street': street,
                "city": city,
                "country": country,
                'format': 'json'
            }
            response = requests.get(locationiq_url, params=data)
            d = json.loads(response.text)[0]
            address = d["display_name"]
            longitude = float(d["lon"])
            latitude = float(d["lat"])

        else:
            street = None
            city = None
            country = None
            longitude = None
            latitude = None

        # create volunteer object
        volunteer = Volunteer(
            number=number,
            street=street,
            city=city,
            country=country,
            longitude=longitude,
            latitude=latitude,
            morning=is_available_morning,
            afternoon=is_available_afternoon,
            evening=is_available_evening
        )

        # check to see if number already in list
        reg_volunteer = Volunteer.query.filter_by(number=volunteer.number).first()

        if reg_volunteer is not None:
            db.session.delete(reg_volunteer)
            db.session.add(volunteer)
            db.session.commit()
            return redirect(
                url_for('update_volunteer', number=volunteer.number))

        else:
            db.session.add(volunteer)
            db.session.commit()
            return redirect(
                url_for('add_volunteer', number=volunteer.number))

    return render_template("getdata.html")


@app.route('/update_volunteer')
def update_volunteer():
    number = request.args.get('number')

    reg_volunteer = Volunteer.query.filter_by(number=number)
    data = reg_volunteer.first().serialize()

    return render_template(
        'update_volunteer.html',
        data=data,
        sandbox_number=sandbox_number,
        sandbox_code=sandbox_code
    )


@app.route('/add_volunteer')
def add_volunteer():
    number = request.args.get('number')

    reg_volunteer = Volunteer.query.filter_by(number=number)
    data = reg_volunteer.first().serialize()

    return render_template(
        'add_volunteer.html',
        data=data,
        sandbox_number=sandbox_number,
        sandbox_code=sandbox_code
    )


@app.route("/helpme", methods=['GET', 'POST'])
def add_client_form():
    """
    Example:

    https://3fb61cb3.ngrok.io/helpme
    """

    if request.method == "POST":
        number = request.form.get('number').replace(" ", "")   # remove spaces
        street = request.form.get('street')
        city = request.form.get('city')
        country = request.form.get('country')
        order = request.form.get('order')
        date = request.form.get('date')
        morning = request.form.get('morning') != None
        afternoon = request.form.get('afternoon') != None
        evening = request.form.get('evening') != None
        if not morning and not afternoon and not evening:
            morning = True
            afternoon = True
            evening = True

        if street == "":
            street = None
        if city == "":
            city = None
        if country == "":
            country = None
        if street is not None and city is not None and country is not None:
            # geolocate
            data = {
                'key': os.environ.get('LOCATIONIQ_TOKEN'),
                'street': street,
                "city": city,
                "country": country,
                'format': 'json'
            }
            response = requests.get(locationiq_url, params=data)
            d = json.loads(response.text)[0]
            address = d["display_name"]
            longitude = float(d["lon"])
            latitude = float(d["lat"])

        else:
            street = None
            city = None
            country = None
            longitude = None
            latitude = None

        # create client object
        client = Client(
            number=number,
            street=street,
            city=city,
            country=country,
            longitude=longitude,
            latitude=latitude,
            morning=morning,
            afternoon=afternoon,
            evening=evening,
            order=order,
            date=date
        )

        # check to see if number already in list
        reg_client = Client.query.filter_by(number=client.number).first()

        if reg_client is not None:
            db.session.delete(reg_client)
            db.session.add(client)
            db.session.commit()
            return redirect(
                url_for('update_client', number=client.number))
        else:
            db.session.add(client)
            db.session.commit()
            return redirect(
                url_for('add_client', number=client.number))

    return render_template("help.html")


@app.route('/update_client')
def update_client():
    number = request.args.get('number')

    reg_client = Client.query.filter_by(number=number)
    data = reg_client.first().serialize()

    return render_template(
        'update_client.html',
        data=data,
        sandbox_number=sandbox_number,
        sandbox_code=sandbox_code
    )


@app.route('/add_client')
def add_client():
    number = request.args.get('number')

    reg_client = Client.query.filter_by(number=number)
    data = reg_client.first().serialize()

    return render_template(
        'add_client.html',
        data=data,
        sandbox_number=sandbox_number,
        sandbox_code=sandbox_code
    )
