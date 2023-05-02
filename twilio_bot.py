import os
import re
import requests
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

# Twilio Account SID and Auth Token
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']

# Twilio phone number
twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']

# OpenAI API key from Heroku env
openai_api_key = os.environ['openai_api_key']

@app.route('/', methods=['POST'])
def webhook():
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')
    # Generate a response using OpenAI's API
    response_text = generate_response(incoming_msg)

    # Send the generated response as a reply to the incoming SMS
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    twilio_client.messages.create(
        body=response_text,
        from_=twilio_phone_number,
        to=sender
    )

    return jsonify({'success': True}), 200

def generate_response(text):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
                "model": "gpt-3.5-turbo",
                "messages": [{
                    "role": "system",
                    "content": "You're the designated drinking buddy wingman. Avoid liability and giving medical advice and never encourage bad behaviour. Use Gen-Z language and tone. Be weary of trolls. Answer things only related to partying/alcohol/nightlife. For hangovers, suggest DHM, ginger, milk thistle, prickly pear. Ensure responses under 100 tokens."},
                             {"role": "user", "content": text}],
                "temperature":0.2,
                "max_tokens":100
        }
    )
    print(f"API response: {response.json()}")
    response_text = response.json()['choices'][0]['message']['content']
    #print(response_text)
    return response_text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
# Receive a payload from Postscript when they text "BonsaiBuddy" and reply with a text from our Twilio number
@app.route('/bonsaibuddy', methods=['POST'])
def send_AI():
    twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
    twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']

    # Twilio phone number
    twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']
    # Extract the message from the request
    payload = request.json
    phone_number=payload.phone_number

    AI_TC = 'Hey its me BonsaiBuddy! Reply YES to confirm you are over 21'
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    twilio_client.messages.create(
        body=AI_TC,
        from_=twilio_phone_number,
         to=phone_number
    )

    return jsonify({'success': True}), 200