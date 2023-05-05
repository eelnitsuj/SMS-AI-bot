import os
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
app = Flask(__name__)
@app.route('/', methods=['POST'])
def send_AI():
    twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
    twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']

    # Extract the message from the request
    #payload = request.json
    #print(payload)
    #phone_number = payload.get('phone_number')
    #print(phone_number)
    # Check the content type and extract the data accordingly
    content_type = request.content_type or 'application/json'

    if content_type == 'application/json':
        try:
            payload = request.json
        except ValueError:
            return jsonify({'error': 'Invalid JSON'}), 400
    elif content_type == 'application/x-www-form-urlencoded':
        payload = request.form
    else:
        return jsonify({'error': 'Invalid content type'}), 403
    
    AI_TC = 'Hey its me Bonnie'
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    twilio_client.messages.create(
        body=AI_TC,
        from_=twilio_phone_number,
        to=+16265326868
    )

    return jsonify({'success': True}), 200