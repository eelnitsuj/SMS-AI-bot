import os
import requests
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

app = Flask(__name__)

# Replace this with your Google Cloud project ID
project_id = 'superbonsai-sms'

# Replace this with your Cloud Pub/Sub topic name
topic_name = 'SMS'

# Replace these values with your own
openai_api_key = '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'

@app.route('/', methods=['POST'])
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
        response_text = generate_response(message['data'])
        #send_response(response_text, message['recipient'])
        #send_email(response_text, message['sender'])

        return jsonify({'success': True}), 200

def generate_response(text):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "system", "content": "You are an AI apothecary and people want to contact you for your wisdom about earth’s natural bounties and cures."},
                             {"role": "user", "content": {text}}
                             ],
                "temperature":0.2,
                "max_tokens":100
        }

    )
    response_text = response.json()['choices'][0]['message']['content'].strip()
    return response_text


def send_response(response_text, recipient):
    # Replace this with your SMS API call to send the response to the recipient
    print(f'Sending message "{response_text}" to {recipient}')

def send_email(subject, body, to, info):
    # Load the credentials from the environment variable
    creds = Credentials.from_authorized_user_info(info)

    # Create the Gmail API client
    service = build('gmail', 'v1', credentials=creds)

    # Define the email message
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    # Send the email
    try:
        message = (service.users().messages().send(userId='me', body=create_message).execute())
        print(F'Sent message to {to} Message Id: {message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        message = None
    return message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
