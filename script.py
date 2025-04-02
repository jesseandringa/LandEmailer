import time
from datetime import date

import pandas as pd

import GmailService as GS
import SpreadsheetService as SS
import util.NewsScraper as NS
from GmailService import GmailService



def load_data(csv_file):
    """Load and prepare CSV data for email processing."""
    data = pd.read_csv(csv_file)
    dont_data = pd.read_csv("dontEmailList.csv")
    retry_data = pd.read_csv("retries.csv")
    
    # Add needed columns if they don't exist
    if "Tried Emailing" not in data.columns:
        data["Tried Emailing"] = [""] * len(data)
    if "Email Sent" not in data.columns:
        data["Email Sent"] = [""] * len(data)
        
    # Set up don't email list columns if needed
    if "State" not in dont_data.columns:
        dont_data["State"] = [""] * len(dont_data)
    if "County" not in dont_data.columns:
        dont_data["County"] = [""] * len(dont_data)
        
    return data, dont_data, retry_data

def should_send_email(email, row_index, data, dont_emails, retry_emails, emails_used):
    """Determine if an email should be sent based on various criteria."""
    if email in dont_emails or pd.isna(email):
        return False
    if data["Email Sent"].iloc[row_index] == "Yes":
        return False
    if data["Tried Emailing"].iloc[row_index] == "Yes":
        return False
    if email in retry_emails and email in emails_used:
        return False
    return True





def land_script():
    """Main function to process and send land purchase emails."""
    print("Starting land email campaign")
    
    # Get user inputs
    sender_email = input("Enter the email address you want to send from: ")
    if sender_email == '':
        sender_email= 'swellagroupllc@gmail.com'
    csv_file = input("Enter the CSV file name containing the recipient data: ")
    if csv_file == '':
        csv_file = 'Park and fremont county 2_19_2025 - Sheet1 (1).csv'
    number_of_emails = int(input("How many emails do you want to send? "))
    if number_of_emails == '':
        number_of_emails = 1
    # Initialize Gmail service
    gmail_service = GmailService(sender_email)
    
    # Load data
    data, dont_data, retry_data = load_data(csv_file)
    retry_emails = list(retry_data["emails"])
    dont_emails = list(dont_data["Emails"])
    
    # Track progress
    emails_sent = 0
    emails_used = []
    consecutive_errors = 0
    errors_allowed = 3
    
    # Process each email
    for i in range(len(data)):
        email = data["Email 1"].iloc[i]
        
        # Skip if we shouldn't send to this email
        if not should_send_email(email, i, data, dont_emails, retry_emails, emails_used):
            continue
            
        # Get recipient information
        first_name = data["First Name"].iloc[i]
        last_name = data["Last Name"].iloc[i]
        county = data["County"].iloc[i]
        state = data["State"].iloc[i]
        parcel_number = data["Parcel Number"].iloc[i]
        
        # Mark as tried
        data.loc[i, "Tried Emailing"] = "Yes"
        
        # Send the email
        try:
            if number_of_emails == 1: 
                email = 'casey.andringa@gmail.com'
            print(first_name,last_name,county,state,parcel_number,email)
            success, message = gmail_service.send_email(
                first_name, last_name, county, state, parcel_number, email
            )
            
            if success and number_of_emails != 1:
                emails_used.append(email)
                data.loc[i, "Email Sent"] = "Yes"
                consecutive_errors = 0
                print(f"Successfully sent email to {email}")
            else:
                if number_of_emails !=1: 
                    data.loc[i, "Email Sent"] = str(message)
                    consecutive_errors += 1
                    print(f"Failed to send email to {email}: {message}")
                
        except Exception as e:
            if number_of_emails != 1: 
                print(f"Error sending email to {email}: {str(e)}")
                data.loc[i, "Email Sent"] = f"Exception: {str(e)}"
                consecutive_errors += 1
        
        # Add to don't email list
        if email not in ["bumpdog@gmail.com", "casey.andringa@gmail.com"]:
            dont_data.loc[len(dont_data.index)] = [email, "emailed before", state, county]
        
        # Check if we've hit error limit
        if consecutive_errors >= errors_allowed:
            response = input("There have been multiple consecutive errors. Continue? (Y/N) ")
            if response.upper() != "Y":
                break
            consecutive_errors = 0
        
        # Add delay between emails
        time.sleep(30)
        
        # Increment counter and check limit
        emails_sent += 1
        print(f"Emails sent: {emails_sent}/{number_of_emails}")
        if emails_sent >= number_of_emails:
            break
    
    # Check for delivery failures
    has_failures, failed_emails = gmail_service.check_mail_delivery_errors()
    if has_failures:
        print(f"Delivery failures detected for: {failed_emails}")
        for email in failed_emails:
            data.loc[data["Email 1"] == email, "Email Sent"] = "** Address Doesn't Exist **"
    
    # Save updated data
    data.to_csv(csv_file, index=False)
    dont_data.to_csv("dontEmailList.csv", index=False)
    print(f"Email campaign completed. Sent {emails_sent} emails.")


def makeSSChanges():
    print("changes script")
    # data = pd.read_csv('GunisonLandUpdated.csv')
    data = pd.read_csv("retries.csv")
    emailss = data["emails"]
    emailer = GS.EmailService(
        "bumpdog@gmail.com",
        emailss,
        ["bumpdog@gmail.com"],
        ["counties"],
        ["EMAILS"],
        "state",
    )
    unread_emails = emailer.gmail.get_unread_inbox()
    print(unread_emails[0].plain)

    emailsList = []
    for message in unread_emails:
        print(type(message.plain))
        es = emailer.getEmailAddressFromMessage(message.plain)
        # if len(es) > 1:
        # cont = input("more than 1 email found" + str(es) + "add all? Y/N")
        # if cont == "N":
        # continue
        emailsList.extend(es)

    cont = input("done... emails: " + str(emailsList) + "add all to csv? Y/N")
    if cont == "Y":
        for em in emailsList:
            data.loc[len(data.index)] = [em]
        data.to_csv("retries.csv", index=False)


if __name__ == "__main__":
    # print(sys.executable)
    # script = input(
        # "What script are you running? Type one of these: \n land\n spreadsheet\n"
    # )
    # if script == "land":
    land_script()
    # if script == "spreadsheet":
    #     makeSSChanges()

# data = {
#     'DataZapp_Email': ['bumpdog@gmail.com','bumpdog@gmail.com','bumpdofsdfsdfsdfsdfsfg@gmail.com','jess.andringa@gmail.com','bumpdog@gmail.com'],
#     'Owner First' : ['Jesse','Jesse','Jesse','JESSE','Jesse'],
#     'Owner Last' : ['Andringa','Andringa','Andringa', 'ANDROW','Andringa'],
#     'PARCEL NO' : ['2222','99999999','112321121', '123432141','000002202'],
#     'County' : [ 'denver','boulder','boulder,','slc', 'denver'],
#     'DataZapp_DoNotCall': ['','','yes','','yes']
# }
