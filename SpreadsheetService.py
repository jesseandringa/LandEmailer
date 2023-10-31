


from __future__ import print_function
import gspread
import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BREWERY_LIST_URL='https://www.coloradobrewerylist.com/brewery/'
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1xC4XMIWnCcn2ioWBWVfxaVqsvcPyGSv3221evCVlejw'
RANGELINK = 'Sheet1!A24'
RANGE = 'Sheet1!A1:H150'



# def cleanSpreadSheet(columns, currentDontLike, desiredClean, type = 'String'):
#     if type == 'String':
#         for index, column in enumerate(columns):
#             if column 

            
def getSpreadsheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        return sheet, service
    except HttpError as err:
        print(err)
        return ''
def getSpreadsheetValues(sheet):
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE,
                                    valueRenderOption='UNFORMATTED_VALUE').execute()
        values = result.get('values', [])
  
        if not values:
            print('No data found.')
            return ''
            
    except HttpError as err:
        print(err)
        
    return values

### cell: String of cell/ range of cells ex: 'A1' or 'A1:C3'
### values in list of lists [[value]] if one cell
def updateRow(cell, values, sheet):
    range = 'Sheet1!'+cell 

    # Prepare the value to be updated
    value_input_option = 'RAW'  # You can also use 'USER_ENTERED' for formulas, formatting, etc.

    # Update the value of the specified cell
    try:
        request = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range,
            valueInputOption=value_input_option,
            body={'values': values}
        ).execute()
    except HttpError as e:
        print('\nwaiting 1 minute \n')
        time.sleep(60)
        request = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range,
            valueInputOption=value_input_option,
            body={'values': values}
        ).execute()
        
        
        
    
    # print('Updated cell:', request['updatedRange'])

def getRow(row, sheet):
    rowRange = 'Sheet1!A'+str(row)+':H'+str(row)
    print(rowRange)
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=rowRange,
                                    valueRenderOption='UNFORMATTED_VALUE').execute()
        row = result.get('values', [])
        
        if not row:
            print('No data found.')
            return ''

        print('row: ' + str(row))
        for data in row:
            
            print(str(data))
            
    except HttpError as err:
        print(err)
        
    return row[0]

def getBrewingListUrlFromRow(row):
    if not row: 
        return ''
    
    breweryName = row[0]
    if breweryName == '': 
        return 
    # print(breweryName)
    breweryName = str(breweryName)
    linkName = breweryName.replace(' &', '')
    linkName = linkName.replace('.','')
    linkName = linkName.replace('(','')
    linkName = linkName.replace(')','')
    linkName = linkName.replace(' ','-')
    url = BREWERY_LIST_URL + linkName + '/'
    
    # print(url)
    return url
    
    
    
if __name__ == '__main__':
    sheet,service = getSpreadsheet()
    if sheet != '':
        values = getSpreadsheetValues(sheet)
    #     values = getRow(24, sheet)
    #     getBrewingListUrlFromRow(values)
    # if values != '':
    #     for row in values: 
    #         break
    # cell = 'E4:F5'
    # values = [[5,6]]
             
    
    
 
























