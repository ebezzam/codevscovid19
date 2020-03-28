# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
# import urllib.request
import requests


app = Flask(__name__)


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
        # urllib.request.urlretrieve(media_url, "image.jpg")
        # import pudb
        # pudb.set_trace()
        r = requests.get(media_url, allow_redirects=True, stream=True)
        with open("local-filename.jpg", 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        resp.message("Got your picture!")

    else:

        resp.message("Ahoy! Thanks so much for your message.")

    return str(resp)


if __name__ == "__main__":
    print("go to : http://127.0.0.1:5000/whatsapp")
    app.run(debug=True)
