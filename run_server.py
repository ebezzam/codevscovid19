# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
import json
from graph import Volunteers, Customers
import SimpleEvent.events
from twilio.rest import Client


app = Flask(__name__)

locationiq_url = "https://us1.locationiq.com/v1/reverse.php"

# to maintain the data of all the customers and volunteers. 
# They are dictionary with phone number as key.
vols = Volunteers()
cuts = Customers()

# hack to test when have one phone number to test
vol_timings = {'1':'Morning','2':'Afternoon','3':'Evening'}
cust_timings = {'a':'Morning','b':'Afternoon','c':'Evening'}

# to send custom message
account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_TOKEN')
client = Client(account_sid, auth_token)

@app.route("/whatsapp", methods=['GET', 'POST'])
def whatsapp_parser():
    """Respond to incoming messages."""

    # Extract info from message
    text = request.values.get('Body', None)
    longitude = request.values.get("Longitude", None)
    latitude = request.values.get("Latitude", None)
    number = request.values.get("From", None)
    n_media = int(request.values.get("NumMedia"))

    # assuming the volunteer's message starts with "volunteer" and
    # customer's with "customer"
    
    # dummy reply
    reply_for_text = "Ahoy! Thanks so much for your message."

    # when message is text
    if text is not None:

        # update the list of customers
        if text.lower() == "customer":
            cuts.update_data({'phone_num':number},vols.active_vol_list)
            reply_for_text = "Your number is registered as a Customer. Tell us your possible delivery timings. \n Send A for Morning 8am-12pm \n B for Afternoon 12pm-4pm \n C for Evening 4pm-8pm\n You can choose multiple timings."
        
        # update the list of volunteers
        elif text.lower() == "volunteer":
            vols.update_data({'phone_num':number},cuts.active_cust_list)
            reply_for_text = "Your number is registered as a Volunteer. Tell us your availability. \n Send 1 for Morning 8am-12pm \n 2 for Afternoon 12pm-4pm \n 3 for Evening 4pm-8pm\n You can choose multiple timings."
        
        # update the particular volunteer's timing
        elif text.split(' ')[0] in ['1','2','3']:
            # assume text to be space separated
            available_times = text.split(' ')
            available_times = [vol_timings[t] for t in available_times]
            vols.update_data({'phone_num':number,'available_times':available_times},cuts.active_cust_list)
            opted_times = ' '.join(available_times)
            reply_for_text = f"Your availability is set for {opted_times}. Please send your location."
        
        # update the particular customer's timing
        elif text.split(' ')[0].lower() in ["a","b","c"]:
            # assume text to be space separated
            available_times = text.split(' ')
            available_times = [cust_timings[t.lower()] for t in available_times]
            cuts.update_data({'phone_num':number,'delivery_by':available_times},vols.active_vol_list)
            opted_times = ' '.join(available_times)
            reply_for_text = f"Your delivery timings are set for {opted_times}. Please take a picture of your grocery list"

    # Start our response
    resp = MessagingResponse()

    # save the grocery list image url 
    if n_media > 0:
        media_url = request.values.get("MediaUrl0")
        cuts.update_data({'phone_num':number,'order':media_url},vols.active_vol_list)

        resp.message(body="Got your picture!. Send us your location.")

    # handling for location and since this the last step in the sequence of instruction, 
    # we try to find a match here        
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

        reply_text_body=f"Your address : {address}."
        
        # check if the location sent was of a customer or volunteer, by comparing the keys.
        if number in cuts.list.keys():
            #update the customer location and receive the match
            vol,cust,time = cuts.update_data({'phone_num':number,'address_info':[longitude,latitude,address_dict]},vols.active_vol_list)
            
            # check if a match was found
            if vol is  None:
                # reply to the customer
                reply_text_body += "We'll get back to you with info of your friendly neighbor."
            else:
                # reply to the customer
                reply_text_body += "Your Neighbor:{} has agreed to do the delivery in the {}. You can get in touch with them.".format(vol.number[9:], time)
                resp.message(body="")
                message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        body= reply_text_body,
                        to='whatsapp:{}'.format(cust.number[9:])
                        )
                print(message.sid)

                # reply to the volunteer
                vol_message = "We found a customer:{} needing your help. Their address is :{}. You can see their grocery list in the image attached to be delivery by the {}".format(cust.number[9:], cuts.get_address(cust.number), time)
               
                message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        body= vol_message,
                        media_url=[cust.order],
                        to='whatsapp:{}'.format(vol.number[9:])
                        )
                print(message.sid)
            resp.message(body=reply_text_body)

        # check if the location sent was of a customer or volunteer, by comparing the keys.
        elif number in vols.list.keys():
            #update customer location and receive the match
            vol,cust,time = vols.update_data({'phone_num':number,'address_info':[longitude,latitude,address_dict]},cuts.active_cust_list)
            
            # check if a match was found
            if vol is  None:
                # reply to the volunteer
                reply_text_body += "Thanks for your help. We'll get back to with the info of the delivery."
                resp.message(body=reply_text_body)
            else:
                # reply to the volunteer
                reply_text_body += "\nThanks for your help. We found {} at this address:{}. Attached is the image of their grocery list to be delivery by the {}.".format(cust.number[9:], cuts.get_address(cust.number), time)
                resp.message(body="")
                message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        body= reply_text_body,
                        media_url= [cust.order],
                        to='whatsapp:{}'.format(vol.number[9:])
                        )
                print(message.sid)

                # reply to the customer
                cust_message = "We found a neighbor:{} ready to help you and make delivery by the {}. You can get in touch with them.".format(vol.number[9:], time)
                message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        body= cust_message,
                        to='whatsapp:{}'.format(cust.number[9:])
                        )
                print(message.sid)
        
    else:
        resp.message(body=reply_for_text)

    return str(resp)


if __name__ == "__main__":
    print("go to : http://127.0.0.1:5000/whatsapp")
    app.run(debug=True)
