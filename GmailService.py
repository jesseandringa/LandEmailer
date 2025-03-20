from simplegmail import Gmail
from simplegmail.query import construct_query
from googleapiclient.errors import HttpError
import re
from datetime import datetime

class GmailService:
    """Service for sending and managing emails through Gmail API."""
    
    def __init__(self, sender_email):
        """
        Initialize the Gmail service with just the sender email.
        
        Args:
            sender_email: Email address of the sender
        """
        self.sender = sender_email
        self.gmail = Gmail()  # Will open browser window for authentication
        
        # Default values that can be set via methods
        self.parcels = []
        self.counties = []
        self.recipients = []
        self.state = 'Utah'
        
        # Email templates
        self.default_subject = 'SLC-based couple hoping to make an offer on vacant land'
    
    def set_property_info(self, parcels=None, counties=None, state=None):
        """
        Set property-related information.
        
        Args:
            parcels: List of parcel identifiers
            counties: List of county names
            state: State name or abbreviation
        
        Returns:
            self (for method chaining)
        """
        if parcels:
            self.parcels = parcels
        
        if counties:
            self.counties = [county.title().replace(' Nm', '') for county in counties]
            
        if state:
            # Standardize state name
            if state == 'NM':
                self.state = 'New Mexico'
            elif state == 'CO':
                self.state = 'Colorado'
            else:
                self.state = state
                
        return self
    
    def set_recipients(self, recipients):
        """
        Set email recipients list.
        
        Args:
            recipients: List of recipient email addresses
            
        Returns:
            self (for method chaining)
        """
        self.recipients = recipients if recipients else []
        return self
    
    def set_email_subject(self, subject):
        """
        Set the email subject line.
        
        Args:
            subject: Subject line for emails
            
        Returns:
            self (for method chaining)
        """
        self.default_subject = subject
        return self
    
    def send_emails(self, company_name, email_list=None):
        """
        Send emails to a list of recipients.
        
        Args:
            company_name: Name of the company or recipient
            email_list: List of email addresses to send to (uses self.recipients if None)
            
        Returns:
            List of email addresses that were successfully sent to
        """
        if email_list is None:
            email_list = self.recipients
            
        failed_emails = set()
        for email in email_list:
            success, _ = self.send_email(company_name, email)
            if not success:
                failed_emails.add(email)
                
        successful_emails = [email for email in email_list if email not in failed_emails]
        return successful_emails
    
    def check_mail_delivery_errors(self):
        """
        Check unread emails for delivery failure notifications.
        
        Returns:
            Tuple of (bool, list): Whether failures were found and list of failed email addresses
        """
        # Query for unread emails that might contain delivery failure notifications
        params = {
            "unread": True,
            "subject": ["failure", "delivery", "undeliverable", "returned"]
        }
        emails = self.gmail.get_messages(query=construct_query(params))
        
        failed_emails = []
        for message in emails:
            message.mark_as_read()
            message_text = message.plain
            
            if any(error_text in message_text for error_text in 
                  ['** Address not found **', 'Message blocked', 'Message not delivered']):
                failed_email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message_text)
                if failed_email:
                    failed_emails.append(failed_email.group())
        
        return len(failed_emails) > 0, failed_emails
    
    def send_email(self, recipient_name, recipient_email, parcels=None, attachments=None):
        """
        Send email to a single recipient.
        
        Args:
            recipient_name: Name of the recipient
            recipient_email: Email address of the recipient
            parcels: List of parcel identifiers (uses self.parcels if None)
            attachments: List of file paths to attach
            
        Returns:
            Tuple of (success, message/error)
        """
        if parcels is None:
            parcels = self.parcels
        if attachments is None:
            attachments = []
            
        recipient_name = recipient_name.title()
        message_html, message_plain = self.create_message(recipient_name, parcels, self.counties)
        
        params = {
            "to": recipient_email,
            "sender": self.sender,
            "subject": self.default_subject,
            "msg_html": message_html,
            "msg_plain": message_plain,
            "signature": True,  # Use account signature
            "attachments": attachments
        }
        
        try:
            message = self.gmail.send_message(**params)
            return True, message
        except HttpError as e:
            error_message = "Error sending email"
            if e.resp.content:
                try:
                    error_details = e.resp.json()["error"]["errors"][0]
                    error_message = f"Error: {error_details.get('message', '')} ({error_details.get('reason', '')})"
                except (ValueError, KeyError, IndexError):
                    error_message = f"HTTP Error: {str(e)}"
            
            return False, error_message
    
    def create_message(self, owner_name, parcels, counties):
        """
        Create email message body in HTML and plain text formats.
        
        Args:
            owner_name: Name of the property owner
            parcels: List of parcel identifiers
            counties: List of county names
            
        Returns:
            Tuple of (HTML body, plain text body)
        """
        html_body = f'''
        <p>Hi! My name's Casey, I'm hoping to reach {owner_name} regarding a parcel of vacant land 
        in the greater Salt Lake/Park City area that I am hoping to make an offer on. My significant 
        other and I are currently looking for our first home down in the Sugarhouse area and have 
        came up empty handed after months of searching. I was starting to get a little sick and tired 
        of playing the exact same house-search game as everyone else, so figured I would reach out to 
        owners of potential parcels we like and see if you would be interested in selling to two folk 
        looking to build a small home to live in while we build our lives in Utah.</p>

        <p>I have no idea if you'd consider selling, but please email me back here or give me a call/text 
        at my cell below anytime if you are (or even know somebody that might).</p>

        <p>Also, sorry if this is the wrong email, or if you are not interested in selling, please let me 
        know and I'll remove you from my list that I made from the county map.</p>

        <p>Thanks!</p>
        '''
        
        # Convert HTML to plain text by removing HTML tags
        plain_body = re.sub(r'<[^>]+>', '', html_body)
        plain_body = re.sub(r'\s+', ' ', plain_body).strip()
        
        return html_body, plain_body
    
    def extract_emails_from_text(self, text):
        """
        Extract email addresses from a text string.
        
        Args:
            text: Text string to search for email addresses
            
        Returns:
            List of email addresses found in the text
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails
    
    def get_sent_emails_and_check_delivery_status(self):
        """
        Get all emails that were sent from the sender today and check if they were delivered or sent to spam.
        
        Returns:
            Tuple of (dict, list): Dictionary of email statuses and list of undelivered emails
        """
        # Get all emails sent today
        today = datetime.now().strftime('%Y-%m-%d')
        emails = self.gmail.get_messages(query=f'after:{today}')
        
        delivery_status = {}
        undelivered_emails = []
        print('emails', emails)
        # Check delivery status of each email
        for email in emails:
            print('email', email)
            recipient = self._extract_recipient_from_email(email)
            if recipient:
                is_delivered = self._check_if_delivered(email)
                delivery_status[recipient] = is_delivered
                if not is_delivered:
                    undelivered_emails.append(recipient)
                print(f"Email to {recipient}: {'Delivered' if is_delivered else 'Not delivered'}")
        
        return delivery_status, undelivered_emails
    
    def _extract_recipient_from_email(self, email):
        """
        Extract recipient email from an email message.
        
        Args:
            email: Email message object
            
        Returns:
            Recipient email address or None
        """
        # Implementation depends on Gmail API's structure
        # This is a placeholder - actual implementation needed
        try:
            if hasattr(email, 'recipient'):
                return email.recipient
            # Fallback to extracting from headers if available
            return None
        except:
            return None
    
    def _check_if_delivered(self, email):
        """
        Check if an email was successfully delivered.
        
        Args:
            email: Email message object
            
        Returns:
            Boolean indicating delivery status
        """
        # Placeholder - actual implementation would depend on Gmail API
        # This would typically check for bounce messages, delivery receipts, etc.
        return hasattr(email, 'is_delivered') and email.is_delivered
    

