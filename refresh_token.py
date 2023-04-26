import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Specify the required scopes
scopes = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

# Start the OAuth flow
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json', scopes)

creds = flow.run_local_server(port=8080)

# Save the credentials to a JSON file for future use
creds_data = {
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
    'refresh_token': creds.refresh_token,
    'token_uri': creds.token_uri
}

with open('credentials.json', 'w') as outfile:
    json.dump(creds_data, outfile)
