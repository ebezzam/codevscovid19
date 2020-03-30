from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse
from graph import Volunteers as GraphVol
from graph import Customers as GraphCust

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
locationiq_url_reverse = "https://us1.locationiq.com/v1/reverse.php"
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


@app.route("/get_clients")
def get_clients():
    """
    Example:

    https://3fb61cb3.ngrok.io/get_clients?pwd=PASSWORD&city=Lausanne

    https://3fb61cb3.ngrok.io/get_clients?pwd=PASSWORD&lon=6.58989274833333&lat=46.5267366&dist=5

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
        reg_client = Client.query.filter(
            and_(
                Client.longitude.between(min_coord.lon, max_coord.lon),
                Client.latitude.between(min_coord.lat, max_coord.lat)
            )
        )
    elif city is not None:
        reg_client = Client.query.filter_by(city=city)
    else:
        raise ValueError("Provide GPS coordinates or city.")

    # build result
    n_clients = reg_client.count()
    result = {
            "n_clients": n_clients
        }

    numbers = reg_client.all()
    clients = []
    for _num in numbers:
        clients.append(_num.serialize())
    result["clients"] = clients
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


""" from VIDIT"""

# to maintain the data of all the customers and volunteers.
# They are dictionary with phone number as key.
vols = GraphVol()
cuts = GraphCust()

# hack to test when have one phone number to test
vol_timings = {'1':'Morning','2':'Afternoon','3':'Evening'}
cust_timings = {'a':'Morning','b':'Afternoon','c':'Evening'}
timings = {'1':'Morning','2':'Afternoon','3':'Evening'}


@app.route("/whatsapp", methods=['GET', 'POST'])
def whatsapp_parser():
    """Respond to incoming messages."""

    # Extract info from message
    text = request.values.get('Body', None)
    longitude = request.values.get("Longitude", None)
    latitude = request.values.get("Latitude", None)
    number = request.values.get("From", None)
    number = number.split(":")[1]
    n_media = int(request.values.get("NumMedia"))

    # assuming the volunteer's message starts with "volunteer" and
    # customer's with "customer"

    # default reply
    reply_for_text = "Hey there! Sorry I didn't understand that.\n" \
                     "Send 'Volunteer' to help.\n" \
                     "Send 'Customer' to get help.\n" \
                     "And we'll guide you through everything else you need to send."

    # when message is text
    if text is not None:

        if text.lower() == "remove":
            reg_volunteer = Volunteer.query.filter_by(number=number).first()
            reg_client = Client.query.filter_by(number=number).first()

            if reg_volunteer is not None or reg_client is not None:
                if reg_volunteer is not None:
                    db.session.delete(reg_volunteer)
                    db.session.commit()
                if reg_client is not None:
                    db.session.delete(reg_client)
                    db.session.commit()
                reply_for_text = "Your number has been removed from our database. " \
                                 "Send 'Volunteer' or 'Customer' to signup again."

            else:
                reply_for_text = "Your number is not in our database."

        # update the list of customers
        if text.lower() == "customer":

            # check to see if already registered as volunteer
            client = Client(number=number)
            reg_client = Client.query.filter_by(number=client.number).first()

            if reg_client is not None:

                info = reg_client.serialize()
                body = [
                    f"*{_key}* : {info[_key]}" for _key in info.keys()
                ]
                body = "\n".join(body)
                reply_for_text = "Your number is already registered as a " \
                                 "Customer. This is the info we have on " \
                                 "you:\n\n" + body
                reply_for_text += "\n\nTo let us know when you want your grocery " \
                                 "delivered, send:\n" \
                                 "*1* for Morning 8am-12pm\n" \
                                 "*2* for Afternoon 12pm-4pm\n" \
                                 "*3* for Evening 4pm-8pm\n" \
                                 "You can choose multiple timings by " \
                                 "separating them with spaces."
                reply_for_text += "\n\nSend your location so we can match you with a volunteer."
            else:
                db.session.add(client)
                db.session.commit()
                # reply_for_text = "Your number is registered as a Customer! " \
                #                  "Send us your location so that we can " \
                #                  "find people nearby to help :)"
                reply_for_text = "Your number is registered as a Customer! " \
                                 "You can unsubscribe by sending 'Remove'." \
                                 "\n\nLet us know when you want your groceries " \
                                 "delivered. Send:\n" \
                                 "*1* for Morning 8am-12pm\n" \
                                 "*2* for Afternoon 12pm-4pm\n" \
                                 "*3* for Evening 4pm-8pm\n" \
                                 "You can choose multiple timings by " \
                                 "separating them with spaces."

            # cuts.update_data({'phone_num': number}, vols.active_vol_list)
            # reply_for_text = "Your number is registered as a Customer. Tell us your possible delivery timings. \n Send A for Morning 8am-12pm \n B for Afternoon 12pm-4pm \n C for Evening 4pm-8pm\n You can choose multiple timings."

        # update the list of volunteers
        elif text.lower() == "volunteer":

            # check to see if already registered as volunteer
            volunteer = Volunteer(number=number)
            reg_volunteer = Volunteer.query.filter_by(
                number=volunteer.number).first()

            if reg_volunteer is not None:

                info = reg_volunteer.serialize()
                body = [
                    f"*{_key}* : {info[_key]}" for _key in info.keys()
                ]
                body = "\n".join(body)
                reply_for_text = "Your number is already registered as a " \
                                 "Volunteer. This is the info we have on " \
                                 "you:\n\n" + body
                reply_for_text += "\n\nLet us know when you can help. Send:\n" \
                                 "*1* for Morning 8am-12pm\n" \
                                 "*2* for Afternoon 12pm-4pm\n" \
                                 "*3* for Evening 4pm-8pm\n" \
                                 "You can choose multiple timings by " \
                                 "seperating them with spaces."
                reply_for_text += "\n\nSend your location so we can match you with someone who needs help."

            else:
                db.session.add(volunteer)
                db.session.commit()
                # reply_for_text = "Your number is registered as a Volunteer! " \
                #                  "Send us your location so we can connect " \
                #                  "you with people that need help."
                reply_for_text = "Your number is registered as a Volunteer! " \
                                 "You can unsubscribe by sending 'Remove'." \
                                 "\n\nLet us know when you can help. Send:\n" \
                                 "*1* for Morning 8am-12pm\n" \
                                 "*2* for Afternoon 12pm-4pm\n" \
                                 "*3* for Evening 4pm-8pm\n" \
                                 "You can choose multiple timings by " \
                                 "seperating them with spaces."

        # update the particular volunteer's timing
        elif text.split(' ')[0] in ['1', '2', '3']:

            available_times = text.split(' ')
            available_times = [timings[t] for t in available_times]

            reg_volunteer = Volunteer.query.filter_by(number=number).first()
            reg_client = Client.query.filter_by(number=number).first()
            if reg_client is not None:
                user = reg_client
            elif reg_volunteer is not None:
                user = reg_volunteer
            else:
                user = None

            if user is not None:
                if "Morning" in available_times:
                    user.morning = True
                if "Afternoon" in available_times:
                    user.afternoon = True
                if "Evening" in available_times:
                    user.evening = True

            else:
                reply_for_text = "Hey there! Your number doesn't seem to be " \
                                 "registered.\n" \
                                 "Send 'Volunteer' to help.\n" \
                                 "Send 'Customer' to get help.\n" \
                                 "And we'll guide you through everything " \
                                 "else you need to send."

            if user is not None:
                available_times = []
                if user.morning:
                    available_times.append("Morning")
                if user.afternoon:
                    available_times.append("Afternoon")
                if user.evening:
                    available_times.append("Evening")
                opted_times = ', '.join(available_times)
                if reg_volunteer is not None:
                    reply_for_text = f"Your availability: " \
                                     f"{opted_times}.\nPlease send your location."

                else:
                    reply_for_text = f"Your delivery slots: " \
                                     f"{opted_times}.\nPlease take a picture of your grocery list."

            db.session.commit()

            # # assume text to be space separated
            # available_times = text.split(' ')
            # available_times = [vol_timings[t] for t in available_times]
            # vols.update_data(
            #     {'phone_num': number, 'available_times': available_times},
            #     cuts.active_cust_list)
            # opted_times = ' '.join(available_times)
            # reply_for_text = f"Your availability is set for {opted_times}. Please send your location."

        # # update the particular customer's timing
        # elif text.split(' ')[0].lower() in ["a", "b", "c"]:
        #     # assume text to be space separated
        #     available_times = text.split(' ')
        #     available_times = [cust_timings[t.lower()] for t in
        #                        available_times]
        #     cuts.update_data(
        #         {'phone_num': number, 'delivery_by': available_times},
        #         vols.active_vol_list)
        #     opted_times = ' '.join(available_times)
        #     reply_for_text = f"Your delivery timings are set for {opted_times}. Please take a picture of your grocery list"

    # Start our response
    resp = MessagingResponse()

    # save the grocery list image url
    if n_media > 0:

        reg_client = Client.query.filter_by(number=number).first()

        if reg_client is not None:
            media_url = request.values.get("MediaUrl0")
            reg_client.order = media_url
            db.session.commit()
            # cuts.update_data({'phone_num': number, 'order': media_url},
            #                  vols.active_vol_list)

            resp.message(body="Got your picture!. Send us your location.")
        else:
            resp.message(body="Hmm we don't seem to have you set up as "
                              "a customer. Send 'Customer' to get started."
                         )

    # handling for location and since this the last step in the sequence of instruction,
    # we try to find a match here
    elif longitude is not None:

        # check for register user
        vol = Volunteer.query.filter_by(number=number).first()
        cust = Client.query.filter_by(number=number).first()

        if cust is not None:
            user = cust
        elif vol is not None:
            user = vol
        else:
            user = None
            reply_text_body = "Hey there! Your number doesn't seem to be " \
                              "registered.\n" \
                              "Send 'Volunteer' to help.\n" \
                              "Send 'Customer' to get help.\n" \
                              "And we'll guide you through everything " \
                              "else you need to send."

        # parse location info
        data = {
            'key': os.environ.get('LOCATIONIQ_TOKEN'),
            'lat': str(latitude),
            'lon': str(longitude),
            'format': 'json'
        }
        response = requests.get(locationiq_url_reverse, params=data)
        d = json.loads(response.text)
        address = d["display_name"]
        address_dict = d["address"]

        # save in database
        user.country = address_dict["country"]
        user.city = address_dict["city"]
        user.street = address_dict["house_number"] + " " + address_dict["road"]
        user.longitude = longitude
        user.latitude = latitude

        reply_text_body = f"Saved the following address : {address}."
        db.session.commit()

        resp.message(body=reply_text_body)

        # # check if the location sent was of a customer or volunteer, by comparing the keys.
        # if number in cuts.list.keys():
        #     # update the customer location and receive the match
        #     vol, cust, time = cuts.update_data({'phone_num': number,
        #                                         'address_info': [longitude,
        #                                                          latitude,
        #                                                          address_dict]},
        #                                        vols.active_vol_list)
        #
        #     # check if a match was found
        #     if vol is None:
        #         # reply to the customer
        #         reply_text_body += "We'll get back to you with info of your friendly neighbor."
        #     else:
        #         # reply to the customer
        #         reply_text_body += "Your Neighbor:{} has agreed to do the delivery in the {}. You can get in touch with them.".format(
        #             vol.number[9:], time)
        #         resp.message(body="")
        #         message = client.messages.create(
        #             from_='whatsapp:+14155238886',
        #             body=reply_text_body,
        #             to='whatsapp:{}'.format(cust.number[9:])
        #         )
        #         print(message.sid)
        #
        #         # reply to the volunteer
        #         vol_message = "We found a customer:{} needing your help. Their address is :{}. You can see their grocery list in the image attached to be delivery by the {}".format(
        #             cust.number[9:], cuts.get_address(cust.number), time)
        #
        #         message = TwilioClient.messages.create(
        #             from_='whatsapp:+14155238886',
        #             body=vol_message,
        #             media_url=[cust.order],
        #             to='whatsapp:{}'.format(vol.number[9:])
        #         )
        #         print(message.sid)
        #     resp.message(body=reply_text_body)
        #
        # # check if the location sent was of a customer or volunteer, by comparing the keys.
        # elif number in vols.list.keys():
        #     # update customer location and receive the match
        #     vol, cust, time = vols.update_data({'phone_num': number,
        #                                         'address_info': [longitude,
        #                                                          latitude,
        #                                                          address_dict]},
        #                                        cuts.active_cust_list)
        #
        #     # check if a match was found
        #     if vol is None:
        #         # reply to the volunteer
        #         reply_text_body += "Thanks for your help. We'll get back to with the info of the delivery."
        #         resp.message(body=reply_text_body)
        #     else:
        #         # reply to the volunteer
        #         reply_text_body += "\nThanks for your help. We found {} at this address:{}. Attached is the image of their grocery list to be delivery by the {}.".format(
        #             cust.number[9:], cuts.get_address(cust.number), time)
        #         resp.message(body="")
        #         message = client.messages.create(
        #             from_='whatsapp:+14155238886',
        #             body=reply_text_body,
        #             media_url=[cust.order],
        #             to='whatsapp:{}'.format(vol.number[9:])
        #         )
        #         print(message.sid)
        #
        #         # reply to the customer
        #         cust_message = "We found a neighbor:{} ready to help you and make delivery by the {}. You can get in touch with them.".format(
        #             vol.number[9:], time)
        #         message = client.messages.create(
        #             from_='whatsapp:+14155238886',
        #             body=cust_message,
        #             to='whatsapp:{}'.format(cust.number[9:])
        #         )
        #         print(message.sid)

    else:
        resp.message(body=reply_for_text)

    return str(resp)
