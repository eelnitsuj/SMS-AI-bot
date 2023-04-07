import requests
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

# Replace this with your Google Cloud project ID
project_id = 'superbonsai-sms'

# Replace this with your Cloud Pub/Sub topic name
topic_name = 'SMS'

# Replace this with your OpenAI API key
openai_key = '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'

# Replace this with your OpenAI model ID
model_id = 'davinci'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Extract the Cloud Pub/Sub message from the request
        envelope = request.get_json()
        if not envelope:
            return jsonify({'error': 'Invalid request'}), 400

        message = envelope.get('message')
        if not message:
            return jsonify({'error': 'Invalid message'}), 400

        # Process the message (e.g., save to a database, call another API, etc.)
        response = process_message(message)
        send_response(response, message.get('sender'))

        return jsonify({'success': True}), 200

def process_message(message):
    # Add your logic to process the message here
    user_message = message.get('text')
    
    # Call the OpenAI API to generate a response
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_key}',
    }
    data = {
        'model': model_id,
        'prompt': user_message,
        'temperature': 0.5,
        'max_tokens': 50,
    }
    response = requests.post('https://api.openai.com/v1/engines/davinci-codex/completions', headers=headers, json=data)
    
    # Extract the response text from the OpenAI API response
    if response.status_code == 200:
        response_text = response.json()['choices'][0]['text']
    else:
        response_text = 'Sorry, I could not understand your message. Please try again.'
    
    return response_text

def send_response(response_text, recipient):
    # Replace this with your SMS API call to send the response to the recipient
    print(f'Sending message "{response_text}" to {recipient}')

@app.route("/", methods=["GET"])
def test_webhook():
    data = {
        "message": {
            "data": "Test data",
            "sender": "+1234567890"
        }
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = app.test_client().post("/webhook", json=data, headers=headers)
    return f"Webhook response: {response.status_code}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
