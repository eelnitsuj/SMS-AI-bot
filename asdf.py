import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Postscript API key
postscript_api_key = os.environ['postscript_api_key']

@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Extract the message from the request
        envelope = request.get_json()
        
        # Extract the sender phone number and message content
        sender = envelope.get('phone_number', '')
        message = envelope.get('message', '')

        if not envelope:
            return jsonify({'error': 'Invalid request'}), 403

        # Generate a response using the GPT-3 API
        response_text = generate_response(message)

        # Send the response using the Postscript API
        send_sms(sender, response_text)

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
    #print(response_text)
    return response_text

def send_sms(to, message_body):
    # Implement the Postscript API SMS sending logic here

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
