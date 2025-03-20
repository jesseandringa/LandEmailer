import base64
import os
from email.mime.text import MIMEText

from google.auth.credentials import Credentials  # Import Credentials class
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# Function to authenticate and return Gmail service
def authenticate_user():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # The OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


# Function to send email
def send_email(service, message):
    try:
        send_message = (
            service.users().messages().send(userId="me", body=message).execute()
        )
        print(f'Message Id: {send_message["id"]}')
        return send_message
    except Exception as error:
        print(f"An error occurred: {error}")


# Function to create the email message
def create_message(sender, to, subject, body):
    message = MIMEText(body)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw_message}


# Authenticate the first test user
creds_user_1 = authenticate_user()
service_user_1 = build("gmail", "v1", credentials=creds_user_1)

# Authenticate the second test user (you'd go through the OAuth flow again)
creds_user_2 = authenticate_user()
service_user_2 = build("gmail", "v1", credentials=creds_user_2)

# Send email from the first test user
sender_1 = "swellagroupllc@gmail.com"
to = "bumpdog@gmail.com"
subject = "Test email from User 1"
body = "This is a test email from the first test user."
message_1 = create_message(sender_1, to, subject, body)
send_email(service_user_1, message_1)

# Send email from the second test user
sender_2 = "theswellagroupllc@gmail.com"
subject = "Test email from User 2"
body = "This is a test email from the second test user."
message_2 = create_message(sender_2, to, subject, body)
send_email(service_user_2, message_2)
