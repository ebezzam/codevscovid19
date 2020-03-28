# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
import json


app = Flask(__name__)

locationiq_url = "https://us1.locationiq.com/v1/reverse.php"


@app.route("/whatsapp", methods=['GET', 'POST'])
def whatsapp_parser():
    """Respond to incoming messages."""

    # Extract info from message
    text = request.values.get('Body', None)
    longitude = request.values.get("Longitude", None)
    latitude = request.values.get("Latitude", None)
    number = request.values.get("From", None)
    n_media = int(request.values.get("NumMedia"))

    # Start our response
    resp = MessagingResponse()

    if n_media > 0:
        media_url = request.values.get("MediaUrl0")
        r = requests.get(media_url, allow_redirects=True, stream=True)
        with open("local-filename.jpg", 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        resp.message(body="Got your picture!")

    elif longitude is not None:
        # return corresponding address for now

        data = {
            'key': os.environ.get('LOCATIONIQ_TOKEN'),
            'lat': str(latitude),
            'lon': str(longitude),
            'format': 'json'
        }
        response = requests.get(locationiq_url, params=data)

        d = json.loads(response.text)
        address = d["display_name"]
        address_dict = d["address"]
        house_number = address_dict["house_number"]
        road = address_dict["road"]
        city = address_dict["city"]
        country = address_dict["country"]

        resp.message(body=f"Your address : {address}")

    else:

        resp.message(body="Ahoy! Thanks so much for your message.")

    return str(resp)


if __name__ == "__main__":
    print("go to : http://127.0.0.1:5000/whatsapp")
    app.run(debug=True)
