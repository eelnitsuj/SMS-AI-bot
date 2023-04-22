import os
from flask import Flask, request, jsonify
from twilio.rest import Client
from database import create_connection, add_subscriber, remove_subscriber, is_subscriber_opted_in
from openai_api import generate_response

app = Flask(__name__)

# Twilio Account SID and Auth Token
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']

# Twilio phone number
twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']

@app.route('/', methods=['POST'])
def webhook():
    phone_number = request.form.get('From')
    message = request.form.get('Body').strip().upper()

    conn = create_connection('your_database.db')

    if message == "SUPERBONSAI":
        add_subscriber(conn, phone_number)
        response_text = "You have successfully opted in."
    elif message == "STOP":
        remove_subscriber(conn, phone_number)
        response_text = "You have successfully opted out."
    else:
        if is_subscriber_opted_in(conn, phone_number):
            response_text = generate_response(message)
        else:
            response_text = "Please text 'SUPERBONSAI' to opt in."

    # Send the generated response as a reply to the incoming SMS
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    twilio_client.messages.create(
        body=response_text,
        from_=twilio_phone_number,
        to=phone_number
    )

    return jsonify({'success': True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
