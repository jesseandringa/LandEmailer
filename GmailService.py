from simplegmail import Gmail
from simplegmail.query import construct_query
from googleapiclient.errors import HttpError
import re 
import numpy as np
####
class EmailService:
    def __init__(self, my_email_address, addresses, email, cities, email_list, state = 'Colorado'):
        self.sender = my_email_address
        self.gmail = Gmail() # will open a browser window to ask you to log in and authenticate
        self.addresses = addresses
        self.email = email
        self.num_of_addresses = len(addresses)
        for i in range(len(cities)):
            if cities[i] is None or not isinstance(cities[i], str) or len(cities[i]) < 2:
                cities[i] = state.upper()
            else:
                cities[i] = cities[i].lower()
                cities[i] = cities[i].title()
        self.cities = [county for county in cities]
        self.all_emails = email_list 
        self.state = state
      
    def getEmailsWithQuery(self, query):
        messages = self.gmail.get_messages(query=construct_query(query))
        return messages
        
    # send email to list of emails
    def sendEmails(self, companyName, emailList):
        failedEmails = set()
        for email in emailList:
            worked = self.sendEmail(companyName, email)
            if not worked: 
                failedEmails.add(email)
        workedEmails = list(filter(lambda email: email not in failedEmails, emailList))
        return workedEmails
    
    #looks at unread emails to see if email was unable to be found
    def checkMailDeliveryError(self, emails):
        some_failed= False
        failed_emails = []
        for message in emails: 
            message.mark_as_read()
            # print("To: " + message.recipient)
            # print("From: " + message.sender)
            # print("Subject: " + message.subject)
            # print("Date: " + message.date)
            # print("Preview: " + message.snippet)
            print("Message Body: " + message.plain)
            
            if '** Address not found **' in message.plain or "Message blocked" in message.plain or "Message not delivered" in message.plain:
                failed_email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message.plain)
                if failed_email: 
                    print('failed email ' +failed_email.group())
                    failed_emails.append(failed_email.group())
                    some_failed = True 
                # print(f'address not found: {self.email}')
                
        return some_failed, failed_emails
                
            
            
    #send email to single email  
    def sendEmail(self,name,emailAddress, addresses ,attachments = []):
        ''' use simplegmail library to send email to email 
            given name of person and emailaddress
        '''
        print("sendEmail", name, emailAddress, addresses)
        name = name.title()
        messageHTMLBody,messageBodyPlain = self.makeMessage(name, addresses, self.cities)
        subject ='New land investor looking to purchase your parcel of vacant land'
        params = {
            "to": emailAddress,
            "sender": self.sender,
            "subject": subject,
            "msg_html": messageHTMLBody,
            "msg_plain": messageBodyPlain,
            "signature": True, # use my account signature
            "attachments": attachments
        }
        print("params", params)
        try:
            message = self.gmail.send_message(**params) 
            print(f'http error:::: {message}')
            return (True,message)
        except HttpError as e:
            print('HTTP ERRORRRRR')
            if e.resp.content:
                error_details = e.resp.json()["error"]["errors"][0]
                error_message = error_details["message"]
                error_reason = error_details["reason"]
                
                print("An HttpError occurred:")
                print(f"Error Message: {error_message}")
                print(f"Error Reason: {error_reason}")
                print(f"email: "+emailAddress)
            else:
                print('HTTP error with email: ' + emailAddress)
            error_mess =  str(error_message) + str(error_reason) 
            return (False, error_mess)
        
        
    def makeMessage(self, owner_name, addresses, cities):
        pattern  = r'^\d'
        if re.match(pattern, addresses[0]):
            address_component = f'the address of the parcel is {addresses[0]}'
        else:
            address_component = f'the parcel is off of {addresses[0]}'


        HTMLBody = f'<p>Hi! My name’s Casey, I’m hoping to reach {owner_name} regarding a parcel of vacant land in  {cities[0]} that I am hoping to make an offer on ({address_component}) <p>'

        HTMLBody +=f'<p>Also, I know theres a ton of email scams out there, so if you feel better calling or texting me, here’s my cell (303)-618-6175.<p>'
 

        HTMLBody +=f'<p>I’m new to land investing and have been looking in the greater {cities[0]} area, for a few weeks and think yours could be a good fit. I have no idea if you would be interested in selling, but if you are, I’d love to chat further and see if we can find a price that works for both of us. I (and the partners I’ve worked with in the past) typically just pay in cash so the transaction is faster and easier on all parties.<p>'

        HTMLBody +=f'<p>Thanks for your time, and if this is the wrong email address, or you simply don’t want to sell, my apologies for wasting your time! I look forward to hearing from you! Also, If you don’t want me to contact you again, please just let me know.<p>'
        
        plainBody = str(HTMLBody)
        plainBody = re.sub(r'<p>|<\/p>', '', plainBody)
        
        return HTMLBody, plainBody
    
    def getEmailAddressFromMessage(self,message):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Use re.findall to find all email addresses in the message
        emails = re.findall(email_pattern, message)

        return emails

###########
# Not part of the class
#################
# send email to list of emails
def sendEmails(companyName, emailList):
    failedEmails = set()
    for email in emailList:
        worked = sendEmail(companyName, email)
        if not worked: 
            failedEmails.add(email)
    workedEmails = list(filter(lambda email: email not in failedEmails, emailList))
    return workedEmails
      
#send email to single email  
# def sendEmail(companyName,emailAddress):
#     gmail = Gmail() # will open a browser window to ask you to log in and authenticate
    
#     messageHTMLBody,messageBodyPlain = makeMessage(companyName)
    
#     params = {
#         "to": emailAddress,
#         "sender": "c0mmerciallycreativ3@gmail.com",
#         "subject": "Product Photo Opportunity",
#         "msg_html": messageHTMLBody,
#         "msg_plain": messageBodyPlain,
#         "signature": True, # use my account signature
#         "attachments":["Commercially_Creative_Product_Deck.pdf"]
#     }
#     try:
#         message = gmail.send_message(**params) 
#         # print(message)
#         return (True, 'None')
#     except HttpError as e:
#         if e.resp.content:
#             error_details = e.resp.json()["error"]["errors"][0]
#             error_message = error_details["message"]
#             error_reason = error_details["reason"]
            
#             print("An HttpError occurred:")
#             print(f"Error Message: {error_message}")
#             print(f"Error Reason: {error_reason}")
#             print(f"email: "+emailAddress)
#         else:
#             print('HTTP error with email: ' + emailAddress)
#         error_mess =  str(error_message) + str(error_reason) 
#         return (False, error_mess)