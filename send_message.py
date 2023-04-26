import requests

url = "https://api.postscript.io/api/v2/message_requests"

payload = {
    "country": "US",
    "category": "promotional"
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": "Bearer sk_d295fe89a5ec7cd1a81a4a7daf01ca0d"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)