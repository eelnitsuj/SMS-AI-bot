import os
import requests
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

# Replace this with your Google Cloud project ID
project_id = 'superbonsai-sms'

# Replace this with your Cloud Pub/Sub topic name
topic_name = 'SMS'

# Replace these values with your own
openai_api_key = 'your_openai_api_key'
gmail_user = 'your_gmail_address'
gmail_password = 'your_gmail_password'

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
        response_text = generate_response(message['data'])
        send_response(response_text, message['recipient'])
        send_email_response(response_text, message['sender'])

        return jsonify({'success': True}), 200

def generate_response(text):
    # Replace this with your OpenAI API call to generate a response
    prompt = "Conversation with a customer:\n" + text + "\nResponse:"
    response = requests.post(
        'https://api.openai.com/v1/engines/davinci-codex/completions',
        headers={'Authorization': f'Bearer {openai_api_key}'},
        json={
            'prompt': prompt,
            'max_tokens': 50,
            'n': 1,
            'stop': 'User:',
            'temperature': 0.7,
        },
    )
    response_text = response.json()['choices'][0]['text'].strip()
    return response_text

def send_response(response_text, recipient):
    # Replace this with your SMS API call to send the response to the recipient
    print(f'Sending message "{response_text}" to {recipient}')

def send_email_response(response_text, sender):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = sender
    msg['Subject'] = 'Response to your message'

    body = response_text
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, sender, text)
        print(f'Sent response email to {sender}')
        server.quit()
    except Exception as e:
        print(f'Error: {e}')
        print('Unable to send response email')

@app.route("/", methods=["GET"])

def test_webhook():
    data = {
        "message": {
            "data": "Test data",
        },
        "sender": "test@example.com",
        "recipient": "1234567890"
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = app.test_client().post("/webhook", json=data, headers=headers)
    return f"Webhook response: {response.status_code}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
