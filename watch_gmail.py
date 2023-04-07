import os
import google.auth
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# Set up OAuth 2.0 authentication
def authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", ["https://www.googleapis.com/auth/gmail.modify",
                                        "https://www.googleapis.com/auth/pubsub"]
            )
            creds = flow.run_local_server(host="localhost", port=8080)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds
# Set up Gmail "watch"
def watch_gmail(creds, pubsub_topic):
    try:
        service = build("gmail", "v1", credentials=creds)
        request = {
            "labelIds": ["INBOX"],
            "topicName": pubsub_topic,
        }
        response = service.users().watch(userId="me", body=request).execute()
        print(f"Successfully set up watch on Gmail. Expiration: {response['expiration']}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        response = None

    return response

if __name__ == "__main__":
    # Replace this with the full topic name you created in Cloud Pub/Sub
    pubsub_topic = "projects/superbonsai-sms/topics/SMS"

    credentials = authenticate()
    watch_gmail(credentials, pubsub_topic)
