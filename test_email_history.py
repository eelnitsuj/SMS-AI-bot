from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os

load_dotenv()  # Load the variables from .env file


def get_gmail():
    creds = Credentials.from_authorized_user_info(info={
        "client_id": os.environ['client_id'],
        "client_secret": os.environ['client_secret'],
        "refresh_token": os.environ['refresh_token'],
        "token_uri": "https://oauth2.googleapis.com/token",
    })

    return build('gmail', 'v1', credentials=creds)


def get_emails_from_sender(service, sender):
    try:
        query = f"from:{sender}"
        response = service.users().messages().list(userId='me', q=query).execute()
        messages = response.get('messages', [])
        email_conversations = []

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_conversations.append(msg)

        last_150 = email_conversations[-150:]
        return last_150
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def main():
    sender_email = "conversations+293285851@mg.postscriptapp.com"
    service = get_gmail()
    email_conversations = get_emails_from_sender(service, sender_email)

    if email_conversations:
        print(f"Total emails from {sender_email}: {len(email_conversations)}")
        for email in email_conversations:
            print(f"Subject: {email['snippet']}\n")
    else:
        print("No emails found.")


if __name__ == '__main__':
    main()
