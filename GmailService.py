from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import os
import re
from datetime import datetime

class GmailService:
    """Service for sending and managing emails through Gmail API."""
    
   
    
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.compose",
    ]
    USERNAME_TO_PORT ={
        "swellagroupllc": 50633,
        "theswellagroupllc": 8080
    }
    
    def __init__(self, sender_email):
        """
        Initialize the Gmail service with sender's email.
        
        Args:
            sender_email: Full email address of the sender (e.g., "example@gmail.com")
        """
        self.sender = sender_email
        self.username = sender_email.split('@')[0]  # Extract username from email
        self.service = self._authenticate_user()
    
    def _authenticate_user(self):
        """Authenticate user and create Gmail service."""
        creds = None
        # The file token.json stores the user's access and refresh tokens.
        token_path = "creds/token_"+self.username + ".json"
        credentials_path = "creds/credentials_" +self.username +".json"
        
        if os.path.exists(token_path):
            print("token path exists")
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        if not creds or not creds.valid:
            print('no creds')
            if creds and creds.expired and creds.refresh_token:
                print('old')
                creds.refresh(Request())

            else:
                print('new')
                # The OAuth flow to get new credentials
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=self.USERNAME_TO_PORT[self.username])
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return  build("gmail", "v1", credentials=creds)
    
    def _create_message(self, to, subject, html_body, plain_body):
        """Create email message in proper format."""
        message = MIMEText(html_body, 'html')
        message['to'] = to
        message['from'] = self.sender
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {"raw": raw_message}
    
    def send_email(self, first_name, last_name, county, state, parcel_number, recipient_email):
        """Send an email to a single recipient."""
        html_body, plain_body = self.create_message(first_name, last_name, county, state, parcel_number)
        subject = f'Interested in purchasing your parcel of land in {county} County, {state}'
        
        message = self._create_message(recipient_email, subject, html_body, plain_body)
        
        try:
            result = self.service.users().messages().send(userId="me", body=message).execute()
            print(f"Message sent successfully. Message ID: {result.get('id')}")
            return True, result
        except Exception as e:
            error_message = f"Failed to send email: {str(e)}"
            print(error_message)
            return False, error_message
    
    def create_message(self, first_name, last_name, county, state, parcel_number):
        """Create email message body in HTML and plain text formats."""
        html_body = f"""
        <p>Hi {first_name}, I hope you're doing well. My name is Casey, and I'm reaching out because 
        I'm interested in purchasing land in {county} County, {state}. I came across your property 
        (Parcel number {parcel_number}) and wanted to see if you might be open to selling. If I have 
        the wrong email, or you simply don't want me to contact you again, please let me know.</p>

        <p>I understand that selling land can be a big decision, and I want to make the process as 
        easy as possible for you. If you're interested, I'd be happy to discuss a potential cash 
        offer with no commissions or closing costs on your end.</p>

        <p>Let me know if you'd like to chat or have any questions—I'd love to hear from you. 
        If you're not interested, just reply and let me know, and I won't contact you again.</p>

        <p>Thank you for your time, and I look forward to hearing from you!</p>
        <p>Casey</p>
        <p>Swella Group LLC</p>
        <p>P.O. Box 16602 Salt Lake City ut 84116</p>
        <p>(801)-923-4989</p>
        """
        
        plain_body = re.sub(r'<[^>]+>', '', html_body)
        return html_body, plain_body
    
    def check_mail_delivery_errors(self):
        """Check unread emails for delivery failure notifications."""
        try:
            # Query for unread emails with failure notifications
            query = "is:unread subject:(failure OR delivery OR undeliverable OR returned)"
            results = self.service.users().messages().list(userId="me", q=query).execute()
            messages = results.get('messages', [])
            
            failed_emails = []
            for msg in messages:
                # Get the full message details
                message = self.service.users().messages().get(userId="me", id=msg['id']).execute()
                
                # Mark as read
                self.service.users().messages().modify(
                    userId="me",
                    id=msg['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                
                # Extract message content
                if 'data' in message['payload']['body']:
                    content = base64.urlsafe_b64decode(
                        message['payload']['body']['data'].encode('ASCII')
                    ).decode('utf-8')
                    
                    if any(error_text in content for error_text in 
                          ['Address not found', 'Message blocked', 'Message not delivered']):
                        failed_email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', content)
                        if failed_email:
                            failed_emails.append(failed_email.group())
            
            return bool(failed_emails), failed_emails
            
        except Exception as e:
            print(f"Error checking delivery failures: {e}")
            return False, []