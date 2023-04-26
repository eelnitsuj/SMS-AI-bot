import requests
import os

openai_api_key = os.environ['openai_api_key']
conversation_history = []

def generate_response(text):
    global conversation_history

    add_message_to_history("user", text)

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Content-Type': 'application/json', 
                'Authorization': f'Bearer {openai_api_key}'},
        json={
            "model": "gpt-3.5-turbo",
            "messages": conversation_history,
            "temperature": 0.2,
            "max_tokens": 100
        }
    )

    response_text = response.json()['choices'][0]['message']['content']

    add_message_to_history("assistant", response_text)

    return response_text

def add_message_to_history(role, content):
    global conversation_history
    conversation_history.append({"role": role, "content": content})
