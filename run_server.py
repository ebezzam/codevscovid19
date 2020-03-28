# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route("/whatsapp", methods=['GET', 'POST'])
def whatsapp_ahoy_reply():
    """Respond to incoming messages."""
    # Start our response
    resp = MessagingResponse()

    # Add a message
    resp.message("Ahoy! Thanks so much for your message.")

    return str(resp)


if __name__ == "__main__":
    print("go to : http://127.0.0.1:5000/whatsapp")
    app.run(debug=True)
