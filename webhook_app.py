import os
import re
import requests
import base64
import json
import pickle
import time
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google_auth_oauthlib.flow import InstalledAppFlow




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
        # Extract email content from the envelope
        email_content = envelope.get('body_plain', '')
        messages = remove_text(email_content)
        print(messages)
        # Extract the sender email
        sendercarrots = envelope.get('Return-Path', '')
        sender = re.findall(r'<(.+?)>', sendercarrots)[0]
        print(sender)
        # Extract the threadId
        threadId = envelope.get('thread_id', '')
        print(threadId)
        if not envelope:
            return jsonify({'error': 'Invalid request'}), 400

        # Send the email message to OPENAI's API
        response_text = generate_response(messages)
        #Send Openai's response to gmail
        send_email(sender,response_text,threadId)

        return jsonify({'success': True}), 200

def generate_response(text):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "system", "content": "You are an AI apothecary and people want to contact you for your wisdom about earth’s natural bounties and cures. I am sending you the entire message conversation history between the customer and you. Make sure the responses are under 100 tokens"},
                             {"role": "user", "content": text}
                             ],
                "temperature":0.2,
                "max_tokens":100
        }
    )
    response_text = response.json()['choices'][0]['message']['content'].strip()
    print(response_text)
    return response_text

def send_email(to, message_body, threadId):
    # Authenticate with Gmail API
    creds = Credentials.from_authorized_user_info(info={
        "client_id": os.environ['client_id'],
        "client_secret": os.environ['client_secret'],
        "refresh_token": os.environ['refresh_token'],
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    service = build('gmail', 'v1', credentials=creds)

    # Construct the message payload
    message = MIMEText(message_body)
    message['to'] = to
    message['subject'] = ''
    message['threadId'] = threadId

    try:
        # Send the reply message
        send_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"Message Id: {send_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None

    return send_message



def remove_text(input_string):
    pattern = r'(?s)On .+?wrote:'
    modified_string = re.sub(pattern, '', input_string)
    while re.search(pattern, modified_string):
        modified_string = re.sub(pattern, '', modified_string)
    # Remove excessive newlines
    modified_string = re.sub(r'\n{2,}', '\n', modified_string)
    return modified_string

def get_gmail():
    creds = Credentials.from_authorized_user_info(info={
        "client_id": os.environ['client_id'],
        "client_secret": os.environ['client_secret'],
        "refresh_token": os.environ['refresh_token'],
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    return build('gmail', 'v1', credentials=creds)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)