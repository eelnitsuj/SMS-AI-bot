import os
import re
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
from google_auth_oauthlib.flow import InstalledAppFlow
import redis

app = Flask(__name__)

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = redis.from_url(redis_url)

# Google Cloud project ID
project_id = 'superbonsai-sms'

# Cloud Pub/Sub topic name
topic_name = 'SMS'

@app.route('/', methods=['POST'])
def postscript_webhook():
    if request.method == 'POST':
        postscript_data = request.get_json()
        sms_text = postscript_data.get('data', {}).get('event_data', {}).get('body', '')

        # Send the SMS text to OpenAI API to get a response
        response_text = generate_response(sms_text)

        # Save the response_text in Redis with an expiration time (e.g., 300 seconds)
        r.setex('response_text', 300, response_text)

    return jsonify({'success': True}), 200

@app.route('/gmail-webhook', methods=['POST'])
def gmail_webhook():
    if request.method == 'POST':
        gmail_data = request.get_json()
        message_data = gmail_data.get('message', {}).get('data', '')

        if message_data:
            decoded_data = base64.urlsafe_b64decode(message_data)
            email_data = json.loads(decoded_data)
            email_address = email_data.get('emailAddress', '')

            # Retrieve the response_text from Redis
            response_text = r.get('response_text')

            if response_text:
                # Send the response_text as an email reply to the email_address
                send_email(email_address, response_text)

    return jsonify({'success': True}), 200


def webhook():
    if request.method == 'POST':
        # Extract the message from the request
        envelope = request.get_json()
        
        # Extract the sender email
        sendercarrots = envelope.get('from', {})
        sender = sendercarrots.get('email','')
        #print(sender)

        # Make sure it's not a reply
        unacceptable_email = 'urbanboyclothes@gmail.com'
        unacceptable_email_2 = 'alerts@mail.zapier.com'

        if sender in (unacceptable_email, unacceptable_email_2, 'alerts+noreply@mail.zapier.com'):
            return jsonify({'error': 'Stop talking to yourself!'}), 468


        # Extract email content from the envelope
        email_content = envelope.get('body_plain', '')
        messages = remove_text(email_content)
        print(messages)

        #Make sure it's not a reaction text
        invalid_starts = ["Loved “", "Liked “", "Disliked “", "Laughed “", "Emphasized “", "Questioned “"]
        if any(messages.startswith(phrase) for phrase in invalid_starts):
            return jsonify({'error': 'Just a reaction'}), 469

        # Extract the threadId
        threadId = envelope.get('thread_id', '')
        #print(threadId)

        if not envelope:
            return jsonify({'error': 'Invalid request'}), 403
        
        #Authenticate GMAIL API
        service=get_gmail()
        #Grab the message history
        message_history=get_emails_from_sender(sender, service)
        print(sender)
        print(message_history)
        # Send the email message to OPENAI's API
        response_text = generate_response(messages, message_history)
        #Send Openai's response to gmail
        send_email(sender,response_text,threadId, service)
        return jsonify({'success': True}), 200

def generate_response(text, message_history):
    openai_api_key = os.environ['openai_api_key']
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

def send_email(to, message_body, threadId, service):
    # Replace newline characters before creating the MIMEText object
    message_body = message_body.replace('\n', ' ').replace('\r', '')

    # Construct the message payload
    message = MIMEText(message_body)
    message['to'] = to
    message['subject'] = ''
    message['threadId'] = threadId

    # Convert the MIMEText object to a raw string (base64 encoded)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    try:
        # Send the reply message
        send_message = service.users().messages().send(userId='me', body={'raw': raw_message, 'threadId': threadId}).execute()
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

def get_emails_from_sender(sender, service):
    try:
        query = f"from:{sender}"
        response = service.users().messages().list(userId='me', q=query).execute()
        messages = response.get('messages', [])
        
        email_snippets = []

        for message in messages[:3]:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            snippet = msg.get('snippet', '')
            email_snippets.append(snippet)

        email_conversations = "\n".join(email_snippets)
        return email_conversations
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
