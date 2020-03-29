from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import json

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
locationiq_url = "https://us1.locationiq.com/v1/search.php"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
sandbox_number = "+14155238886"
sandbox_code = "join lower-parent"

from volunteer import Volunteer


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/add/volunteer")
def add_volunteer():
    """
    Example:

    http://127.0.0.1:5000/volunteer?number=%2B16503051656
    """
    number = request.args.get('number')
    street_number = request.args.get('street_number')
    street = request.args.get('street')
    city = request.args.get('city')
    country = request.args.get('country')
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    is_available_am = request.args.get('is_available_am')
    is_available_pm = request.args.get('is_available_pm')

    # create volunteer object
    volunteer = Volunteer(
        number=number,
        street_number=street_number,
        street=street,
        city=city,
        country=country,
        longitude=longitude,
        latitude=latitude,
        is_available_am=is_available_am,
        is_available_pm=is_available_pm,
    )

    # check to see if number already in list
    reg_volunteer = Volunteer.query.filter_by(number=volunteer.number).first()

    if reg_volunteer is not None:
        db.session.delete(reg_volunteer)
        db.session.add(volunteer)
        db.session.commit()
        return f"{number} already in volunteer list. Updating with new info."

    else:
        db.session.add(volunteer)
        db.session.commit()
        return f"Added {number} to volunteer list. " \
               f"For your first mission, from WhatsApp send '{sandbox_code}' " \
               f" to: {sandbox_number}"


@app.route("/delete_number")
def delete_number():
    """
    Example:

    http://127.0.0.1:5000/delete?number=%2B16503051656
    """

    number = request.args.get('number')
    reg_volunteer = Volunteer.query.filter_by(number=number).first()

    if reg_volunteer is not None:
        db.session.delete(reg_volunteer)
        db.session.commit()
        return f"Removed {number} from database."
    else:
        return f"{number} was not in database."


@app.route("/delete", methods=['GET', 'POST'])
def remove():
    """
    Example:

    https://3fb61cb3.ngrok.io/delete
    """

    if request.method == "POST":
        number = request.form.get('number').replace(" ", "")  # remove spaces
        reg_volunteer = Volunteer.query.filter_by(number=number).first()

        if reg_volunteer is not None:
            db.session.delete(reg_volunteer)
            db.session.commit()
            return f"Removed {number} from database."
        else:
            return f"{number} is not in database."

    return render_template("delete.html")


@app.route("/volunteer", methods=['GET', 'POST'])
def add_volunteer_form():
    """
    Example:

    https://3fb61cb3.ngrok.io/volunteer
    """

    if request.method == "POST":
        number = request.form.get('number').replace(" ", "")   # remove spaces
        # street_number = request.form.get('street_number')
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
            # street_number=street_number,
            street=street,
            city=city,
            country=country,
            longitude=longitude,
            latitude=latitude,
            is_available_am=is_available_morning,
            is_available_pm=is_available_afternoon or is_available_evening,
        )

        # check to see if number already in list
        reg_volunteer = Volunteer.query.filter_by(number=volunteer.number).first()

        if reg_volunteer is not None:
            db.session.delete(reg_volunteer)
            db.session.add(volunteer)
            db.session.commit()
            return f"{number} already in volunteer list. Updating with new info."

        else:
            db.session.add(volunteer)
            db.session.commit()
            return f"Added {number} to volunteer list. " \
                   f"For your first mission, from WhatsApp send '{sandbox_code}' " \
                   f" to: {sandbox_number}"

    return render_template("getdata.html")



