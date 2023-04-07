from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

# Replace this with your Google Cloud project ID
project_id = 'superbonsai-sms'

# Replace this with your Cloud Pub/Sub topic name
topic_name = 'SMS'

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
        process_message(message)

        return jsonify({'success': True}), 200

def process_message(message):
    # Add your logic to process the message here
    print('Received message:', message)

@app.route("/", methods=["GET"])
def test_webhook():
    data = {
        "message": {
            "data": "Test data",
        }
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = app.test_client().post("/webhook", json=data, headers=headers)
    return f"Webhook response: {response.status_code}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
