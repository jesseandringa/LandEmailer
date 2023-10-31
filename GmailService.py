from simplegmail import Gmail
from simplegmail.query import construct_query
from googleapiclient.errors import HttpError
import re 
import numpy as np
####
class EmailService:
    def __init__(self, my_email_address, parcels, email, counties, email_list, state = 'Colorado'):
        self.sender = my_email_address
        self.gmail = Gmail() # will open a browser window to ask you to log in and authenticate
        self.parcels = parcels
        self.email = email
        self.num_of_parcels = len(parcels)
        for i in range(len(counties)):
            counties[i] = counties[i].lower()
            counties[i] = counties[i].title()
        self.counties = [county.replace(' Nm', '') for county in counties]
        self.all_emails = email_list 
        if state == 'NM':
            state = 'New Mexico'
        elif state == 'CO':
            state = 'Colorado'
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
    def sendEmail(self,name,emailAddress, parcels ,attachments = []):
        ''' use simplegmail library to send email to email 
            given name of person and emailaddress
        '''
        name = name.title()
        # print('beforeeeeee')
        messageHTMLBody,messageBodyPlain = self.makeMessage(name, parcels, self.counties)
        # attachments = ["Commercially_Creative_Product_Deck.pdf"]
        subject = 'Inquiring about a land parcel'
        if self.counties[0] != 'xx' and self.counties[0] != ' ':
            subject += ' in '+ str(self.counties[0]) +' county'
        else:
            subject += ' in ' +str(self.state)
        
        # print('message: ::::::::::::::::::::::::::::::::::::')
        # print(f'subject: {subject}')
        # print(f'messageHTMLBody {messageBodyPlain}')
        params = {
            "to": emailAddress,
            "sender": self.sender,
            "subject": subject,
            "msg_html": messageHTMLBody,
            "msg_plain": messageBodyPlain,
            "signature": False, # use my account signature
            "attachments": attachments
        }
        try:
            message = self.gmail.send_message(**params) 
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
        
        
    def makeMessage(self, owner_name, parcels, counties):
        HTMLBody = '<p>Hi! My name\'s Casey, I was hoping to reach ' + owner_name + ' about'
        if len(parcels) > 1: 
            HTMLBody += ' a couple pieces of vacant land in '
        else: 
            HTMLBody +=' a piece of vacant land in '
        print(f'county {counties[0]}')
        for index , county in enumerate(counties): 
            if len(counties) == 1: 
                if county != 'xx' and county != None and county !=  ' ':
                    HTMLBody+= str(county)+ ' County, '
            else: 
                if index == len(counties) -1:
                    HTMLBody+= str(county) 
                elif index == len(counties) -2: 
                    HTMLBody += str(county) + ' and '
                else:
                    HTMLBody+= str(county) + ", "
                    
            
            
        HTMLBody += self.state + ' that I would like to make an offer on'
        if len(parcels) > 1: 
            HTMLBody += '.<p>'
        else:
            HTMLBody += ' (the parcel number is '+ parcels[0] + ').<p>'
        
        
        HTMLBody += '<p>Also, I know theres a ton of email scams out there, so if you feel better calling or texting me here\'s my cell (303)-618-6175.<p>'
            
        HTMLBody += '<p>My younger brother and I have been actively searching for a piece of land in ' + self.state + ' and I think yours could be just what we\'re looking for! I have no idea if you would be at all interested in selling, but if you are, I\'d love to chat further and see if we can find a price that works for both of us. We\'d be looking to purchase with cash so any proceedings should be pretty quick and painless.<p>'

        HTMLBody += '<p>Thanks for your time, and if this is the wrong email address, my apologies for wasting your time! We look forward to hearing from you!<p>'
        
        plainBody = str(HTMLBody)
        plainBody = re.sub(r'<p>|<\/p>', '', plainBody)
        
        return HTMLBody, plainBody

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
def sendEmail(companyName,emailAddress):
    gmail = Gmail() # will open a browser window to ask you to log in and authenticate
    
    messageHTMLBody,messageBodyPlain = makeMessage(companyName)
    
    params = {
        "to": emailAddress,
        "sender": "c0mmerciallycreativ3@gmail.com",
        "subject": "Product Photo Opportunity",
        "msg_html": messageHTMLBody,
        "msg_plain": messageBodyPlain,
        "signature": True, # use my account signature
        "attachments":["Commercially_Creative_Product_Deck.pdf"]
    }
    try:
        message = gmail.send_message(**params) 
        # print(message)
        return (True, 'None')
    except HttpError as e:
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