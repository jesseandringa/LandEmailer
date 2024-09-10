import time
from datetime import date

import pandas as pd

import GmailService as GS
import SpreadsheetService as SS
import util.NewsScraper as NS


def brewery_script():
    print("brewery script ")
    sheet, service = SS.getSpreadsheet()
    values = SS.getSpreadsheetValues(sheet)
    numOfRows = len(values)
    print(len(values))
    # numOfRows = 52

    # keep track of emails so you don't email same one twice
    Email_Set = set()

    # print('number of rows: ' + str(len(values)))
    for x in range(0, numOfRows):
        row = values[x]

        # if company has not been contacted yet or empty row
        if len(row) > 2 or len(row) < 2:
            continue
            # if no email or not valid email in row, skip row
        # if not NS.validateEmail(row[9]):
        #     continue

        try:
            urlName = SS.getBrewingListUrlFromRow(row)
            name, emailSet = NS.getCompanyNameAndEmail(urlName)

            if name == "Home":
                name = row[0]

            # make sure there are no duplicates of emails being sent
            if name is not None and emailSet is not None:
                print("name: " + name)
                # print(f'email ' + str(emailSet))
                emails = set()
                for email in emailSet:
                    if email in Email_Set:
                        continue
                    emails.add(email)
                    if len(emails) > 3:
                        break

            else:  # update sheet with error
                print("no emaillll")
                today = date.today()
                updateVals = [
                    [today, "Error", "No Email found", "", "", "Jesse Andringa"]
                ]
                SS.updateRow("C" + str(x + 1) + ":H" + str(x + 1), updateVals, sheet)
                continue

            # send email

            workingEmails = GS.sendEmails(name, emails)

            if len(workingEmails) > 0:
                workingEmails = set(workingEmails)
                Email_Set = Email_Set.union(workingEmails)
            else:
                workingEmails = None

            # update sheet
            if workingEmails is not None:
                print(f"loop {x}")
                today = date.today()
                today = str(today)
                updateVals = [
                    [today, "No", str(workingEmails), "", "", "Jesse Andringa"]
                ]
                SS.updateRow("C" + str(x + 1) + ":H" + str(x + 1), updateVals, sheet)
            else:
                print(f"no email in loop {x}")
                today = date.today()
                today = str(today)
                updateVals = [
                    [today, "Error", "Email same as above", "", "", "Jesse Andringa"]
                ]
                SS.updateRow("C" + str(x + 1) + ":H" + str(x + 1), updateVals, sheet)
        except Exception as e:
            print(f"exception in loop {x}")
            today = date.today()
            today = str(today)
            updateVals = [[today, "Error", str(e), "", "", "Jesse Andringa"]]
            SS.updateRow("C" + str(x + 1) + ":H" + str(x + 1), updateVals, sheet)


def land_script():
    print("land script")
    number_of_emails = input("How many emails do you want to send? ")
    number_of_emails = int(number_of_emails)
    MY_EMAIL = "casey.william1994@gmail.com"
    data = pd.read_csv("Salt_lake_summit_county_land_final_v5_final_cleaned.csv")
    dont_data = pd.read_csv("dontEmailList.csv")
    retry_data = pd.read_csv("retries.csv")

    RETRY_EMAILS = retry_data["emails"]
    # EMAILS = data['Email']
    # NAMES = data['FirstName'] +' ' +data['LastName']
    EMAILS = data["Email 1"]
    EMAILS_2 = data["Email 2"]
    NAMES = data["Owner First name"] + " " + data["owner last name"]

    # PARCEL_NUM = data['Parcel Id']
    PARCEL_NUM = data["Parcel Address"]

    # COUNTY = data['Property COUNTY']
    # STATE = data['Property State']
    COUNTY = data["County"]
    STATE = ["Utah"] * len(COUNTY)

    # get column if exists and create it if it doesn't
    try:
        TRIED_EMAILING = data["Tried Emailing"]
        EMAIL_SENT = data["Email Sent"]
    except:
        data["Tried Emailing"] = [""] * len(COUNTY)
        data["Email Sent"] = [""] * len(COUNTY)
        TRIED_EMAILING = data["Tried Emailing"]
        EMAIL_SENT = data["Email Sent"]

    dont_emails = list(dont_data["Emails"])
    emails_used = []
    try:
        DONT_STATE = dont_data["State"]
        DONT_COUNTY = dont_data["County"]
    except:
        dont_data["State"] = [""] * len(dont_emails)
        dont_data["County"] = [""] * len(dont_emails)
        DONT_STATE = dont_data["State"]
        DONT_COUNTY = dont_data["County"]

    amount = 0

    # *errors allowed in a row
    errors_allowed = 3
    for i in range(0, len(EMAILS)):
        print(f"i = {i}")
        if EMAILS[i] not in RETRY_EMAILS:
            # continue
            if EMAILS[i] in dont_emails:
                continue
            if pd.isna(EMAILS[i]):
                continue
            if EMAIL_SENT[i] == "Yes":
                continue
            if TRIED_EMAILING[i] == "Yes":
                continue
            if errors_allowed <= 0:
                errors_allowed_input = input(
                    "There has been 3 errors. Do you want to continue? Y/N "
                )
                if errors_allowed_input != "Y":
                    break
                else:
                    errors_allowed = 3
        elif len(emails_used) > 0:
            print("elselslselsellse")
            if EMAILS[i] in emails_used:
                continue
        else:
            print("11elselsleellelsleleslleslsleleslselselselsellse")
            EMAILS[i] = EMAILS_2[i]

        # get all of the parcels that the owner has

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
            counties = ["xx"]
        # print(parcels)
        # counties = [county for j,email in enumerate(EMAILS) if email == EMAILS[i] for county in [COUNTY[j]]]

        # print(parcels)
        print(counties)

        state = STATE[i]
        # if counties[0] == 'Duschene':
        #     state = 'Utah'
        emailer = GS.EmailService(MY_EMAIL, parcels, EMAILS[i], counties, EMAILS, state)
        for index in same_person_indices:
            TRIED_EMAILING[index] = "Yes"
        # worked = True
        try:
            worked, error_message = emailer.sendEmail(NAMES[i], EMAILS[i], parcels)
            print(f"error_message {error_message}")
        except:
            errors_allowed -= 1
            worked = False
            error_message = "Error in HTTP call"
        print(f"result: {worked} {error_message}")
        if worked:
            emails_used.append(EMAILS[i])
            for index in same_person_indices:
                EMAIL_SENT[index] = "Yes"
            print("worked: " + str(EMAILS[i]))
        else:
            for index in same_person_indices:
                print("error:  " + str(EMAILS[i]))
                EMAIL_SENT[index] = str(error_message)

        if EMAILS[i] != "bumpdog@gmail.com":
            try:
                dont_data.loc[len(dont_data.index)] = [
                    EMAILS[i],
                    "emailed before",
                    state,
                    counties[0],
                ]
            except:
                dont_data.loc[len(dont_data.index)] = [EMAILS[i], "emailed before"]

        amount += 1
        print(f"amount = {amount}")
        if amount >= number_of_emails:
            break

    #### check if we received any system failure emails :
    ## wait a couple mins first for all of them to come in
    print("sleeping")
    time.sleep(20)
    print("done sleeping")
    try:
        unread_emails = emailer.gmail.get_unread_inbox()
        system_error, failed_emails = emailer.checkMailDeliveryError(unread_emails)
    except:
        unread_emails = []
        system_error = False
        failed_emails = []
    print(f"unread emails: {unread_emails}")
    print(f"failed emails: {failed_emails}")
    if system_error:
        #  '** Address doesn\'t exist **'
        for index, item in enumerate(data["Email 1"]):
            if item in failed_emails:
                EMAIL_SENT[index] = "** Address Doesn't Exist **"

    # set columns and update spreadsheet
    # data = pd.DataFrame(data)

    data.to_csv("Salt_lake_summit_county_land_final_v5_final_cleaned.csv", index=False)
    dont_data.to_csv("dontEmailList.csv", index=False)


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
    script = input(
        "What script are you running? Type one of these: \n brewery \n land\n spreadsheet\n"
    )
    if script == "brewery":
        brewery_script()
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
