import os
import requests
import base64
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
    print('Received webhook request')
    if request.method == 'POST':
        # Extract the Cloud Pub/Sub message from the request
        envelope = request.get_json()
        print(envelope)  # Print out the entire envelope to check for the message
        if not envelope:
            return jsonify({'error': 'Invalid request'}), 400

        message = envelope.get('message')
        if not message:
            return jsonify({'error': 'Invalid message'}), 400

        return jsonify({'success': True}), 200
