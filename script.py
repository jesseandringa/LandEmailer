import time

import pandas as pd

import GmailService as GS


def load_data():
    """Load and prepare CSV data for email processing."""
    data = pd.read_csv("Salt_lake_summit_county_land_final_v5_final_cleaned.csv")
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
    # Skip if email is in the don't email list
    if email in dont_emails:
        return False

    # Skip if email is empty
    if pd.isna(email):
        return False

    # Skip if email was already sent successfully
    if data["Email Sent"].iloc[row_index] == "Yes":
        return False

    # Skip if we already tried to email this address
    if data["Tried Emailing"].iloc[row_index] == "Yes":
        return False

    # If this email is in retry list but already used in this session, skip it
    if email in retry_emails and email in emails_used:
        return False

    return True


def get_owner_parcels_and_counties(email, data):
    """Get all parcels and counties for an owner with the given email."""
    same_person_indices = []
    for index, row_email in enumerate(data["Email 1"]):
        if email == row_email:
            same_person_indices.append(index)

    parcels = [data["Parcel Address"].iloc[index] for index in same_person_indices]
    counties = [data["County"].iloc[index] for index in same_person_indices]
    counties = list(set(counties))  # Remove duplicates

    # Handle invalid county data
    if any(isinstance(county, float) for county in counties):
        counties = ["xx"]

    return same_person_indices, parcels, counties


def update_email_status(indices, data, status, message=""):
    """Update the email status for all indices."""
    for index in indices:
        if status:
            data["Email Sent"].iloc[index] = "Yes"
        else:
            data["Email Sent"].iloc[index] = message
        data["Tried Emailing"].iloc[index] = "Yes"


def add_to_dont_email_list(email, state, county, dont_data, reason="emailed before"):
    """Add an email to the don't email list."""
    try:
        dont_data.loc[len(dont_data.index)] = [email, reason, state, county]
    except:
        dont_data.loc[len(dont_data.index)] = [email, reason]


def check_delivery_failures(gmail_service, data):
    """Check for email delivery failures and update status."""
    print("Checking for delivery failures (waiting 20 seconds for emails to arrive)...")
    time.sleep(20)

    try:
        unread_emails = gmail_service.gmail.get_unread_inbox()
        system_error, failed_emails = gmail_service.check_mail_delivery_errors()

        if system_error:
            for index, item in enumerate(data["Email 1"]):
                if item in failed_emails:
                    data["Email Sent"].iloc[index] = "** Address Doesn't Exist **"

        return failed_emails
    except Exception as e:
        print(f"Error checking delivery failures: {e}")
        return []


def save_data(data, dont_data):
    """Save updated data to CSV files."""
    data.to_csv("Salt_lake_summit_county_land_final_v5_final_cleaned.csv", index=False)
    dont_data.to_csv("dontEmailList.csv", index=False)
    print("Data saved successfully.")


def land_script():
    """Main function to process and send land purchase emails."""
    print("Starting land email campaign")

    # Get user input for email limit
    number_of_emails = int(input("How many emails do you want to send? "))
    my_email = "casey.william1994@gmail.com"

    # Initialize the Gmail service with just the sender email
    gmail_service = GS.GmailService(my_email)

    # Load data
    data, dont_data, retry_data = load_data()

    # Extract needed information
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

        # If this email is in retry list but we can't reach it, try Email 2
        print(email)
        raise Exception("test")
        if email in retry_emails and email not in emails_used:
            email = data["Email 2"].iloc[i]

        # Skip if we shouldn't send to this email
        if email not in ["bumpdog@gmail.com", "casey.andringa@gmail.com"]:
            if not should_send_email(
                email, i, data, dont_emails, retry_emails, emails_used
            ):
                continue

        # Get owner information
        name = f"{data['Owner First name'].iloc[i]} {data['owner last name'].iloc[i]}"
        state = data["State"].iloc[i] if "State" in data.columns else "Utah"

        # Get all parcels and counties for this owner
        same_person_indices, parcels, counties = get_owner_parcels_and_counties(
            email, data
        )

        # Configure the Gmail service for this recipient
        gmail_service.set_property_info(parcels, counties, state)
        gmail_service.set_recipients([email])

        # Mark as tried
        update_email_status(same_person_indices, data, False)

        # Send the email
        try:
            print(f"Sending email to {email}")
            raise Exception("test")
            success, error_message = gmail_service.send_email(name, email, parcels)
            print(
                f"Email to {email}: {'Success' if success else f'Failed - {error_message}'}"
            )

            if success:
                emails_used.append(email)
                update_email_status(same_person_indices, data, True)
                consecutive_errors = 0
            else:
                update_email_status(
                    same_person_indices, data, False, str(error_message)
                )
                consecutive_errors += 1
        except Exception as e:
            print(f"Error sending email to {email}: {str(e)}")
            update_email_status(
                same_person_indices, data, False, "Exception: " + str(e)
            )
            consecutive_errors += 1

        # Add to don't email list to avoid future sends
        if email not in ["bumpdog@gmail.com", "casey.andringa@gmail.com"]:
            add_to_dont_email_list(email, state, counties[0], dont_data)

        # Check if we've hit error limit
        if consecutive_errors >= errors_allowed:
            response = input(
                "There have been multiple consecutive errors. Continue? (Y/N) "
            )
            if response.upper() != "Y":
                break
            consecutive_errors = 0

        # Increment counters
        emails_sent += 1
        print(f"Emails sent: {emails_sent}/{number_of_emails}")

        # Check if we've sent enough emails
        if emails_sent >= number_of_emails:
            break

    # Check for delivery failures
    failed_emails = check_delivery_failures(gmail_service, data)
    if failed_emails:
        print(f"Delivery failures detected for: {failed_emails}")

    # Save updated data
    save_data(data, dont_data)
    print(f"Email campaign completed. Sent {emails_sent} emails.")


def makeSSChanges():
    print("changes script")
    # data = pd.read_csv('GunisonLandUpdated.csv')
    data = pd.read_csv("retries.csv")
    emailss = data["emails"]

    # Use the refactored GmailService
    emailer = GS.GmailService("bumpdog@gmail.com")
    emailer.set_recipients(emailss)

    unread_emails = emailer.gmail.get_unread_inbox()
    if unread_emails:
        print(unread_emails[0].plain)

    emailsList = []
    for message in unread_emails:
        print(type(message.plain))
        es = emailer.extract_emails_from_text(message.plain)
        emailsList.extend(es)

    cont = input("done... emails: " + str(emailsList) + "add all to csv? Y/N")
    if cont == "Y":
        for em in emailsList:
            data.loc[len(data.index)] = [em]
        data.to_csv("retries.csv", index=False)


def test_script():
    print("test script")
    emailer = GS.GmailService("casey.william1994@gmail.com")
    emailer.get_sent_emails_and_check_delivery_status()


if __name__ == "__main__":
    # print(sys.executable)
    script = input(
        "What script are you running? Type one of these: \n test \n land\n spreadsheet\n"
    )
    if script == "test":
        test_script()
    if script == "land":
        land_script()
    if script == "spreadsheet":
        makeSSChanges()

# data = {
#     'DataZapp_Email': ['bumpdog@gmail.com','bumpdog@gmail.com','bumpdofsdfsdfsdfsdfsfg@gmail.com','jess.andringa@gmail.com','bumpdog@gmail.com'],
#     'Owner First' : ['Jesse','Jesse','Jesse','JESSE','Jesse'],
#     'Owner Last' : ['Andringa','Andringa','Andringa', 'ANDROW','Andringa'],
#     'PARCEL NO' : ['2222','99999999','112321121', '123432141','000002202'],
#     'County' : [ 'denver','boulder','boulder,','slc', 'denver'],
#     'DataZapp_DoNotCall': ['','','yes','','yes']
# }
