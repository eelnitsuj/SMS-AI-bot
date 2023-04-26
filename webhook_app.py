import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Extract the message from the request
        payload = request.json
        # Grab message body from text
        event_data = payload.get('event_data')
        message = event_data.get('body') if event_data else None

         # Only process messages starting with "Bonsai"
        if message and message.lower().startswith("bonsai"):
            # Grab phone number to reply
            phone_number = event_data.get('from_number') if event_data else None
            print(message)
            print(phone_number)
            # Send the email message to OPENAI's API
            response_text = generate_response(message)
            print(response_text)
            # Send Openai's response back to postscript
            send_text(phone_number, response_text)

            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Ignored non-Bonsai message'}), 200

def generate_response(text):
    openai_api_key = os.environ['openai_api_key']
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
                "model": "gpt-3.5-turbo",
                "messages": [{
                    "role": "system",
                    "content": "You're a Gen-Z drink buddy wingman from NYC. Use familiar lingo, avoid liability, and dodge medical topics. Be cautious of trolls. Focus on partying/nightlife without encouraging bad behavior. Suggest DHM, ginger, milk thistle, and prickly pear for hangovers. Keep responses under 100 tokens and don't ask questions"},
                             {"role": "user", "content": text}],
                "temperature":0.2,
                "max_tokens":100
        }
    )
    #print(f"API response: {response.json()}")
    response_text = response.json()['choices'][0]['message']['content']
    return response_text

def send_text(phone_number, response_text):
    postscript_api_key = os.environ['postscript_api_key']
    url = "https://api.postscript.io/api/v2/message_requests"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f'Bearer {postscript_api_key}'
    }
    payload = {
        "phone":phone_number,
        "body":response_text,
        #"country": "US",
        #"category": "promotional"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return 'Message sent successfully'
    else:
        return f'Error sending message: {response.text}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
