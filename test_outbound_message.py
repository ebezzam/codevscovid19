from twilio.rest import Client
import os

number = ""

account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_TOKEN')
if account_sid is None:
    raise ValueError("Missing TWILIO_SID")
if auth_token is None:
    raise ValueError("Missing TWILIO_TOKEN")
client = Client(account_sid, auth_token)

message = client.messages.create(
    from_='whatsapp:+14155238886',
    body="come back!",
    to='whatsapp:{}'.format(number)
)

print(message.sid)
