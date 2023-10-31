import GmailService as GS
import util.NewsScraper as NS
import SpreadsheetService as SS
from datetime import date 
import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
import numpy as np
import time


def brewery_script():
    print('brewery script ')
    sheet,service = SS.getSpreadsheet()
    values = SS.getSpreadsheetValues(sheet)
    numOfRows = len(values)
    print(len(values))
    # numOfRows = 52
    
    #keep track of emails so you don't email same one twice
    Email_Set = set()
    
    # print('number of rows: ' + str(len(values)))
    for x in range(0,numOfRows):        
        row = values[x]
        
        # if company has not been contacted yet or empty row
        if len(row) > 2 or len(row) < 2:
            continue
            #if no email or not valid email in row, skip row
        # if not NS.validateEmail(row[9]):
        #     continue
        
        try:
            urlName = SS.getBrewingListUrlFromRow(row)
            name, emailSet = NS.getCompanyNameAndEmail(urlName) 
            
            if name == 'Home':
                name = row[0]
                
            #make sure there are no duplicates of emails being sent
            if name is not None and emailSet is not None:
                print('name: '+ name)
                # print(f'email ' + str(emailSet))
                emails = set()
                for email in emailSet: 
                    if email in Email_Set:
                        continue
                    emails.add(email)
                    if len(emails) > 3:
                        break
                        
            else: #update sheet with error
                print('no emaillll')
                today = date.today()
                updateVals = [[today,'Error','No Email found','','','Jesse Andringa']]
                SS.updateRow('C' + str(x+1) + ':H'+ str(x+1),updateVals,sheet)
                continue
                
            #send email
            
            workingEmails = GS.sendEmails(name,emails)
            
            
            if len(workingEmails) >0:
                workingEmails = set(workingEmails)
                Email_Set = Email_Set.union(workingEmails)
            else: 
                workingEmails = None
            
            
            #update sheet
            if workingEmails is not None: 
                print(f'loop {x}')
                today = date.today()
                today = str(today)
                updateVals = [[today,'No',str(workingEmails),'','','Jesse Andringa']]
                SS.updateRow('C' + str(x+1) + ':H'+ str(x+1),updateVals,sheet)
            else:
                print(f'no email in loop {x}')
                today = date.today()
                today = str(today)
                updateVals = [[today,'Error','Email same as above','','','Jesse Andringa']]
                SS.updateRow('C' + str(x+1) + ':H'+ str(x+1),updateVals,sheet)
        except Exception as e:
            print(f'exception in loop {x}')
            today = date.today()
            today = str(today)
            updateVals = [[today,'Error',str(e),'','','Jesse Andringa']]
            SS.updateRow('C' + str(x+1) + ':H'+ str(x+1),updateVals,sheet)
            
            
def land_script():
    print('land script')
    number_of_emails = input("How many emails do you want to send? ")
    number_of_emails = int(number_of_emails)
    MY_EMAIL = 'casey.william1994@gmail.com'
    # numOfRows = 52
    # with open('GunnisonLand.csv',mode='r+') as spreadsheet:
    #     data = csv.DictReader(spreadsheet)
    #     print(f'data '+str(data['DataZapp_Email']))
    data = pd.read_csv('NM_Land.csv')
    dont_data = pd.read_csv('dontEmailList.csv')
    # data = {
    #     'DataZapp_Email': ['bumpdog@gmail.com','bumpdog@gmail.com','bumpdofsdfsdfsdfsdfsfg@gmail.com','jess.andringa@gmail.com','bumpdog@gmail.com'],
    #     'Owner First' : ['Jesse','Jesse','Jesse','JESSE','Jesse'],
    #     'Owner Last' : ['Andringa','Andringa','Andringa', 'ANDROW','Andringa'],
    #     'PARCEL NO' : ['2222','99999999','112321121', '123432141','000002202'],
    #     'County' : [ 'denver','boulder','boulder,','slc', 'denver'],
    #     'DataZapp_DoNotCall': ['','','yes','','yes']
    # }
    
    EMAILS = data['Email']
    # NAMES = data['Owner First'] +' ' +data['Owner Last']
    # NAMES = [first +' ' + last for first,last in zip(data['Owner First'], data['Owner Last'])]
    NAMES = data['FirstName'] +' ' +data['LastName']
    # print(NAMES)
    # if True: 
    #     return
    # print(NAMES)
    PARCEL_NUM = data['Parcel Id']
    # DO_NOT_CALL = data['DataZapp_DoNotCall']
    COUNTY = data['Property COUNTY']
    STATE = data['Property State']
    
    #get column if exists and create it if it doesn't
    try:
        TRIED_EMAILING =  data['Tried Emailing']
        EMAIL_SENT =  data['Email Sent']
    except: 
        data['Tried Emailing'] = [''] * len(COUNTY)
        data['Email Sent'] = [''] * len(COUNTY)
        TRIED_EMAILING =  data['Tried Emailing']
        EMAIL_SENT =  data['Email Sent']
        
    dont_emails = list(dont_data['Emails'])
    emails_used = []
    try:
        DONT_STATE =  dont_data['State']
        DONT_COUNTY =  dont_data['County']
    except: 
        dont_data['State'] = [''] * len(dont_emails)
        dont_data['County'] = [''] * len(dont_emails)
        DONT_STATE =  dont_data['State']
        DONT_COUNTY =  dont_data['County']
    
    amount = 0
   
    # *errors allowed in a row
    errors_allowed = 3
    for i in range(0,len(EMAILS)):
        print(f'i = {i}')
  
        if EMAILS[i] in dont_emails:
            continue
        if pd.isna(EMAILS[i]):
            continue
        if len(emails_used) > 0:
            if EMAILS[i] in emails_used:
                continue
        if EMAIL_SENT[i] == 'Yes':
            continue
        if TRIED_EMAILING[i] == 'Yes':
            continue
        if errors_allowed <= 0: 
            errors_allowed_input = input("There has been 3 errors. Do you want to continue? Y/N ")
            if errors_allowed_input !="Y":
                break
            else: 
                errors_allowed = 3
            
            
        #get all of the parcels that the owner has
        
        # same_person_indices = EMAILS == EMAILS[i]
        # parcels = [parcel for j, email in enumerate(EMAILS) if email == EMAILS[i] for parcel in [PARCEL_NUM[j]]]
        same_person_indices = []
        for index, email in enumerate(EMAILS):
            if EMAILS[i] == email:
                same_person_indices.append(index)
                
        parcels = [PARCEL_NUM[index] for index in same_person_indices]
        counties = [COUNTY[index] for index in same_person_indices]
        counties = list(set(counties))
        
        if any(isinstance(county, float) for county in counties):
            counties = ['xx']
        # print(parcels)
        # counties = [county for j,email in enumerate(EMAILS) if email == EMAILS[i] for county in [COUNTY[j]]]

        # print(parcels)
        print(counties)
        
        state = STATE[i]
        # if counties[0] == 'Duschene':
        #     state = 'Utah'
        emailer = GS.EmailService(MY_EMAIL,parcels,EMAILS[i],counties, EMAILS,state)
        for index in same_person_indices:
            TRIED_EMAILING[index] = 'Yes'
        # worked = True
        try:
            worked,error_message = emailer.sendEmail(NAMES[i], EMAILS[i], parcels)
            # worked = True
            # error_message = 'None'
        except:
            errors_allowed -=1
            worked = False
            error_message = 'Error in HTTP call'
        # worked = True
        # error_message = None
        print(f'result: {worked} {error_message}')
        if worked: 
            emails_used.append(EMAILS[i])
            for index in same_person_indices:
                EMAIL_SENT[index] = 'Yes'
            print('worked: ' +str(EMAILS[i]))
        else:
            for index in same_person_indices:
                print('error:  ' +str(EMAILS[i]))
                EMAIL_SENT[index] = str(error_message)
        # new_dont_row = {'Emails':EMAILS[i],'Reason':'Emailed'}
        if EMAILS[i] != 'bumpdog@gmail.com':
            try:
                dont_data.loc[len(dont_data.index)] = [EMAILS[i], 'emailed before',state,counties[0]] 
            except: 
                dont_data.loc[len(dont_data.index)] = [EMAILS[i], 'emailed before']
                  
        # dont_emails.append(EMAILS[i])
        amount += 1
        print(f'amount = {amount}')
        if amount >=number_of_emails: 
            break
                
        
    #### check if we received any system failure emails : 
    ## wait a couple mins first for all of them to come in
    print('sleeping')
    time.sleep(20)
    print('done sleeping')
    try: 
        unread_emails = emailer.gmail.get_unread_inbox()
        system_error, failed_emails = emailer.checkMailDeliveryError(unread_emails)
    except: 
        unread_emails = []
        system_error = False
        failed_emails = []
    print(f'unread emails: {unread_emails}')
    print(f'failed emails: {failed_emails}')
    if system_error: 
        #  '** Address doesn\'t exist **'
        for index, item in enumerate(data['Email']):
            if item in failed_emails:
                EMAIL_SENT[index] = '** Address Doesn\'t Exist **'
                
           
    #set columns and update spreadsheet
    # data = pd.DataFrame(data)

    data.to_csv('NM_Land.csv',index = False)
    dont_data.to_csv('dontEmailList.csv',index = False)
    #keep track of just emailed people and possible responses
    # sent_info_indices = EMAIL_SENT[:] == 'Yes'
    # names = [names for i,sent in enumerate(EMAIL_SENT) if sent == 'Yes' ]
    # names = NAMES[sent_info_indices]
    # emails  = EMAILS[sent_info_indices]
    # parcs = PARCEL_NUM[sent_info_indices]
    
    
    # record_data = {
    #     'Name' : NAMES,
    #     'Email': EMAILS,
    #     'Parcel Num' : PARCEL_NUM,
    #     'SENT' : EMAIL_SENT
    # }
    # df = pd.DataFrame(record_data)
    # df.to_csv('EmailAndResponseData.csv',index = False)
            

def makeSSChanges():
    print('changes script')
    # data = pd.read_csv('GunisonLandUpdated.csv')
    data = pd.read_csv('NM_Land.csv')
    parcels = data['Parcel Id']
    for i in range(10):
        print(str(parcels[i]))
    
    # EMAILS = data['DataZapp_Email']
    # NAMES = data['Owner First'] +' ' +data['Owner Last']
    # PARCEL_NUM = data['PARCEL NO']
    # DO_NOT_CALL = data['DataZapp_DoNotCall']
    # COUNTY = data['County']
    # TRIED = data['Tried Emailing']
    # REPLIED = data['Replied']
    # INTERESTED = data['Interested']
    # ASKING = data['Asking']
    
    
    # DONT_EMAILS = dont_data['Emails']
    # DONT_REASON = dont_data['Reason']
    
    # try:
    #     DONT_STATE =  dont_data['State']
    #     DONT_COUNTY =  dont_data['County']
    # except: 
    #     dont_data['State'] = [''] * len(DONT_EMAILS)
    #     dont_data['County'] = [''] * len(DONT_EMAILS)
    #     DONT_STATE =  dont_data['State']
    #     DONT_COUNTY =  dont_data['County']
    # for i in range (0,len(DONT_EMAILS)):
    #     DONT_STATE = 'Colorado'
    #     DONT_COUNTY = ''
        
    # for index, email in enumerate(EMAILS):
    #     if TRIED[index] == 'Yes':
    #         new_row = {'Emails':email,'Reason':'emailed before'}
    #         dont_data.loc[len(dont_data.index)] = [email, 'emailed before'] 
            # dont_data = dont_data.append(new_row, ignore_index = True)
    # dont_data = dont_data.drop_duplicates()
    # dont_data.to_csv('dontEmailList.csv',index = False)
            
    # emailer = GS.EmailService('_',['0','1'],'_',['1','1'], ['asdsf','asddf','asfdf'],'Colorado')

    # query_params = {
    #     "newer_than": (2, "day")
    # }
    # messages = emailer.gmail.get_starred_messages()
    # print(f'messages {messages}')

    # for index, message in enumerate(messages):
    #     # print(str(message.sender))
    #     email = str(message.sender)
    #     if email == 'casey.william1994@gmail.com':
    #         continue
    #     if '<' in email: 
    #         match = re.search(r'<(.*?)>', message.sender)
    #         if match:
    #             email = match.group(1)
    #     for i in range(0,len(EMAILS)):
    #         if EMAILS[i] == email:
    #             # print('message' +str(messages[index].snippet))
    #             REPLY[i] = str(messages[index].snippet)
                
    # data.to_csv('GunisonLandUpdated.csv',index = False)

    

if __name__ == '__main__':
    script = input("What script are you running? Type one of these: \n brewery \n land\n spreadsheet\n")
    if script =="brewery":
        brewery_script()
    if script =="land":
        land_script()
    if script =="spreadsheet":
        makeSSChanges()
    
   