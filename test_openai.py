import requests

url = 'https://infinite-castle-46811.herokuapp.com/'
response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    headers={'Content-Type': 'application/json', 
            'Authorization': f'Bearer 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'},
    json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "system", "content": "You are an AI apothecary and people want to contact you for your wisdom about earth’s natural bounties and cures. Make sure the responses are under 100 tokens"},
                            {"role": "user", "content": "Help me get buff!"}
                            ],
            "temperature":0.2,
            "max_tokens":100
    }
)
print(response.json())
#response_text = response.json()['choices'][0]['message']['content'].strip()
#print(response_text)

