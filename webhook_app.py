import os
import requests
import base64
import json
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


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
        print(envelope)
        if not envelope:
            return jsonify({'error': 'Invalid request'}), 400

        #grabs the email address and history ID from pubsub payload
        message_code = envelope['message']['data']
        message_bytes = base64.b64decode(message_code)
        messagepubsub=message_bytes.decode('utf-8')
        print(messagepubsub)
        #uses gmail API to grab email contents from the message ID derived above
        message_id = envelope['message']['messageId']
 
        # Authenticate with Gmail API
        # Authenticate with Gmail API
        with open('credentials.json') as f:
            creds = Credentials.from_authorized_user_info(info=json.load(f))
        service = build('gmail', 'v1', credentials=creds)


        # Get the message using the message ID
        message = service.users().messages().get(userId='me', id=message_id).execute()
        print(message)
        # Extract the message body
        message_body = message['payload']['body']['data']
        print(message_body)
        message_bytes = base64.urlsafe_b64decode(message_body.encode('UTF-8'))
        message_text = message_bytes.decode('UTF-8')
        print(message_text)
        # Send the email message to OPENAI's API
        response_text = generate_response(message_text)



        #Send OPENAI's response via email back to sender. First grab sender_email and subject from pub/sub webhook
        #xmessage = MIMEMultipart()
        #sender_email = xmessage['to']
        #subject = xmessage['subject']
        #send_email(response_text, sender_email, subject)

        return jsonify({'success': True}), 200

def generate_response(text):
    print(text)
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "system", "content": "You are an AI apothecary and people want to contact you for your wisdom about earth’s natural bounties and cures.Make sure the responses are under 100 tokens"},
                             {"role": "user", "content": text}
                             ],
                "temperature":0.2,
                "max_tokens":100
        }
    )
    response_text = response.json()['choices'][0]['message']['content'].strip()
    print(response_text)
    return response_text
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)