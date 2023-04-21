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

conversation_history = []

@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Extract the message from the request
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
    global conversation_history

    # Add user message to conversation history
    add_message_to_history("user", text)

    # API call with conversation history
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
            "model": "gpt-3.5-turbo",
            "messages": conversation_history,
            "temperature": 0.2,
            "max_tokens": 100
        }
    )
    print(conversation_history)
    print(f"API response: {response.json()}")
    response_text = response.json()['choices'][0]['message']['content']

    # Add assistant response to conversation history
    add_message_to_history("assistant", response_text)

    return response_text


def add_message_to_history(role, content):
    global conversation_history
    conversation_history.append({"role": role, "content": content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
