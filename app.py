import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webook():
    user = {}

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    message_time = messaging_event['timestamp'] #timestamp
                    send_message(sender_id, "Got it!")
                    user[sender_id] = {'name':'',
                                       'email': '',
                                       'phone_number': '',
                                       'squash_level': '',
                                       'availability_today':[]}
                    send_message(sender_id, "Got it!")
                    if message_text == 'Hi':
                        send_message(sender_id, "What's your name?")
                        if messaging_event.get("message"):
                            message_text = messaging_event["message"]["text"]
                            user[sender_id]['name'] = message_text
                            send_message(sender_id, "Thanks {0}! What's your hbs email address?")
                            if messaging_event.get("message"):
                                message_text = messaging_event["message"]["text"]
                                if 'mba2017.hbs.edu' in message_text:
                                    user[sender_id]['email'] = message_text
                                    send_message(sender_id, "What's your phone number? (10-digit, numbers only)")
                                    if messaging_event.get("message"):
                                        message_text = messaging_event["message"]["text"]
                                        user[sender_id]['phone_number'] = message_text
                                        send_message(sender_id, "What's your level? (High/Medium/Low)")
                                        if messaging_event.get("message"):
                                            message_text = messaging_event["message"]["text"]
                                            user[sender_id]['level'] = message_text
                                            send_message(sender_id, "What's your availability today? [hh:mm-hh:mm (24-hour format)]")
                                            if messaging_event.get("message"):
                                                message_text = messaging_event["message"]["text"]
                                                user[sender_id]['availability_today'] = message_text


                                else:
                                    send_message(sender_id, "Sorry! Only for HBS 2017! Check again later.")




                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
