import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# OpenAI API key from Heroku env
openai_api_key = os.environ['openai_api_key']

@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Extract the message from the request
        payload = request.json
        print(payload)
        # Grab message body from text
        event_data = payload.get('event_data')
        print(event_data)
        message = event_data.get('body') if event_data else None
        print(message)
        # Send the email message to OPENAI's API
        response_text = generate_response(message)
        print(response_text)
        #Send Openai's response back to postscript
        send_text()

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
                    "content": "You're the designated drinking buddy wingman. Avoid liability and giving medical advice and never encourage bad behaviour. Use Gen-Z language and tone. Be weary of trolls. Answer things only related to partying/alcohol/nightlife. For hangovers, suggest DHM, ginger, milk thistle, prickly pear. Ensure responses under 100 tokens. Here is past message history with the patient:" + message_history},
                             {"role": "user", "content": text}],
                "temperature":0.2,
                "max_tokens":100
        }
    )
    print(f"API response: {response.json()}")
    response_text = response.json()['choices'][0]['message']['content']
    return response_text

def send_text():
    #insert postscript API here
    return 'true'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
