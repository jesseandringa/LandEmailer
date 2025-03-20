import base64
import os
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials  # Import Credentials class
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

email_address_to_port ={
    "swellagroupllc": 50633,
    "theswellagroupllc": 8080
}
# Function to authenticate and return Gmail service
def authenticate_user(email_address):
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    token_path = "token_"+email_address + ".json"
    credentials_path = "credentials_" +email_address +".json"
    
    if os.path.exists(token_path):
        print("token path exists")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        print('no creds')
        if creds and creds.expired and creds.refresh_token:
            print('old')
            creds.refresh(Request())

        else:
            print('new')
            # The OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=email_address_to_port[email_address])
        # Save the credentials for the next run
        with open(token_path, "w") as token:
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

email_address = "swellagroupllc"
# Authenticate the first test user
creds_user_1 = authenticate_user(email_address)
service_user_1 = build("gmail", "v1", credentials=creds_user_1)

# Authenticate the second test user (you'd go through the OAuth flow again)
email_address = "theswellagroupllc"
creds_user_2 = authenticate_user(email_address)
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
