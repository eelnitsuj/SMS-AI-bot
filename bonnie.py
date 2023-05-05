import os
import requests
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from database import get_connection, release_connection


app = Flask(__name__)

# Twilio Account SID and Auth Token
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']

# Twilio phone number
twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']

# OpenAI API key from Heroku env
openai_api_key = os.environ['openai_api_key']

def get_user_status(phone_number):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM user_statuses WHERE phone_number = %s", (phone_number,))
    row = cur.fetchone()
    release_connection(conn)
    return row[0] if row else None

def set_user_status(phone_number, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO user_statuses (phone_number, status) VALUES (%s, %s) ON CONFLICT (phone_number) DO UPDATE SET status = %s", (phone_number, status, status))
    conn.commit()
    release_connection(conn)

@app.route('/a', methods=['POST'])
def webhook():
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')
    user_status = get_user_status(sender)

    if user_status is None:
        if incoming_msg.strip().lower() == 'agree':
            reply(sender,"Thanks for agreeing! What can I help you with?")
            set_user_status(sender, 'active')
            return jsonify({'success': True}), 201
        else:
            reply(sender,"Bonnie here! Before we continue, reply AGREE to acknowledge our T&C to start chatting ")
            return jsonify({'success': True}), 202
    else:
        conversation_history = fetch_conversation_history(sender)
        response_text = generate_response(incoming_msg, conversation_history)
        reply(sender, response_text)

        return jsonify({'success': True}), 200

def generate_response(text,conversation_history):
    system_message = {
    "role": "system",
    "content": "You're the designated drinking buddy wingman. Avoid liability and giving medical advice and never encourage bad behaviour. Use Gen-Z language and tone. Be weary of trolls. Answer things only related to partying/alcohol/nightlife. For hangovers, suggest DHM, ginger, milk thistle, prickly pear. Ensure responses under 100 tokens."
    }
    user_message = {"role": "user", "content": text}
    messages = [system_message] + conversation_history + [user_message]
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 100
        }
    )
    print(f"API response: {response.json()}")
    response_text = response.json()['choices'][0]['message']['content']
    return response_text
def reply(sender,response_text):
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    twilio_client.messages.create(
        body=response_text,
        from_=twilio_phone_number,
        to=sender
    )

def fetch_conversation_history(sender):
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    messages = twilio_client.messages.list(
        to=twilio_phone_number, from_=sender, limit=5
    )
    conversation_history = []
    for message in messages[::-1]:  # Reverse the order of messages, as they are returned in reverse chronological order
        if message.direction == "inbound":
            role = "user"
        else:
            role = "assistant"
        conversation_history.append({"role": role, "content": message.body})

    return conversation_history

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

# Receive a payload from Postscript when they text "Bonnie" and reply with a text from our Twilio number
@app.route('/', methods=['POST'])
def send_AI():
    # Extract the message from the request
    payload = request.json
    print(payload)
    #phone_number = payload.get('phone_number')
    #print(phone_number)

    AI_TC = 'Hey its me Bonnie'
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    twilio_client.messages.create(
        body=AI_TC,
        from_=twilio_phone_number,
        to=+16265326868
    )

    return jsonify({'success': True}), 200