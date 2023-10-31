import requests
from bs4 import BeautifulSoup
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support.relative_locator import locate_with

BREWERY_LIST_URL = 'https://www.coloradobrewerylist.com/brewery/'


HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

def getListOfCompanies():
    response = requests.get(BREWERY_LIST_URL)
    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    brewlist = soup.find('div', class_='brewlist')
    infoSites = brewlist.find_all('a',href=True)
    # print(infoSites)
    return []

def getWebsite(url):
    try:
        response = requests.get(url)
    except:
        url = url.replace('Company','co')
        url = url.replace('company','co')
        try:
            respone = requests.get(url)
        except:
            return None
    soup = BeautifulSoup(response.content,'html.parser')
    website = None
    if soup is not None:
        siteSpan = soup.find('span',class_="website")
        websiteElement= siteSpan.find('a',href=True)
        website = websiteElement['href']
        # print(website)
    return website

def getContactPage(url):
    # print('in getContactPage, '+ url)

    emails = []
    attempts = ['contact','contactus','contact-us','about']
    i = 0
    while len(emails) == 0 and i< len(attempts):
        tempUrl = url + attempts[i]
        i = i+1
        print(tempUrl)
        try:
            response = requests.get(tempUrl, headers=HEADERS)
            soupString = str(response.content)
            match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', soupString)
            print(str(match))
            for m in match: 
                # print(m)
                valid = validateEmail(m)
                # print(valid)
                if valid:
                    emails.append(m)
        except:
            emails = []
            
    
    # print(emails)
    return emails
    
    
def validateEmail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False
    
def checkMainPage(url):
    # print('in checkMainPage '+url)
    # url = 'https://www.14erbrewing.com/'
    # line = "should we use regex more often? let me know at  jdsk@bob.com.lol or popop@coco.com"
    response = requests.get(url, headers=HEADERS)
    # soup = BeautifulSoup(response.content)
    soupString = str(response.content)
    match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', soupString)
    # print(match)
    
    emailList = []
    for m in match: 
        # print(m)
        valid = validateEmail(m)
        # print(valid)
        if valid:
            emailList.append(m)
    # print(emailList)
    return emailList


def getEmail(url):
    # print('in getEmail '+url)

    emails = checkMainPage(url)
    print('mainpage:' +str(emails))
    if len(emails) > 0: 
        emails = list(set(emails))
        return emails
    
    emails = getContactPage(url)
    emails = list(set(emails))
    return emails



def getCompanyName(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    companyName = None
    if soup is not None:
        titleTag = soup.find('title')
        title = titleTag.get_text()
        splitTitle = title.split('–')
        companyName = splitTitle[0]
        companyName = companyName.rstrip()
    # print('companyName: '+companyName)
    return companyName


#method finds element using list of lists of parameters, sends key to that element. 
# it tries all of the fields 2x if not found before returning 
def findElementAndSendKey(driver,fieldsList, key):
    found = False
    attempts = 0
    i = 0
    while not found: 
        try:
            element = driver.find_element(fieldsList[i][0],fieldsList[i][1])
            element.click()
            time.sleep(1)
            if key is not None:
                element.send_keys(key)
            found = True
            print('clicked and filled '+fieldsList[i][1])
        except:
            found = False
            print('except name')
            i = i + 1
            if i> len(fieldsList):
                i = 0
                attempts = attempts + 1
            if attempts > 1:
                found = True
                print('not found '+ str(key))


# waits and looks for popups and accepts them if there. 
def handlePopUps(driver):
    time.sleep(2)
    try:
        WebDriverWait(driver,2).until(expected_conditions.alert_is_present())
    
        if expected_conditions.alert_is_present():
            print('alert is present')
        else:
            print('no alert found')
            
        alert = Alert(driver)
        try:
            alert.accept()
            print('accepted')
        except:
            alert.dismiss()
            print('dismissed')
        print('alert text:  '+ alert.text)
    except:
        print('possible alert found but exception')
    
    try:
        popUp = driver.find_element(By.ID, value="popup-widget394654-close-icon")
        popUp.click()
        print('popUp clicked')
    except:
        print('exception no popup either')

    time.sleep(1)
    
    try:
        WebDriverWait(driver,2).until(expected_conditions.alert_is_present())
    
        if expected_conditions.alert_is_present():
            print('alert is present2')
        else:
            print('no alert found2')
            
        alert = Alert(driver)
        try:
            alert.accept()
            print('accepted')
        except:
            alert.dismiss()
            print('dismissed')
        print('alert text:2  '+ alert.text)
    except:
        print('possible alert found but exception2')
    
        #click age verification::::::
    try:
        ageVerification = driver.find_element(By.ID, "enter")
        ageVerification.click()
        print('age verified')
    except:
        print('no age verifictioan')

        
        
        

    
#takes in a url that should have a contact form to fill out and 
#it fills out the form and send the email
def seleniumFillOutContactForm(url):
    nameFields = [[By.XPATH, "//input[@data-aid='CONTACT_FORM_NAME']"],[By.ID, "ContactForm-name"],[By.NAME,"fname"]]
    emailFields = [[By.XPATH, "//input[@data-aid='CONTACT_FORM_EMAIL']"],[By.ID, "ContactForm-email"],[By.XPATH, "//input[@type='email']"]]
    messageFields = [[By.XPATH, "//textarea[@data-aid='CONTACT_FORM_MESSAGE']"],[By.ID, "ContactForm-body"]]
    submitFields = [[By.XPATH, "//button[@data-aid='CONTACT_SUBMIT_BUTTON_REND']"],[By.CSS_SELECTOR, "button[type='submit']"]]

    # errors = [NoSuchElementException, ElementNotInteractableException]
    driver = webdriver.Chrome()

    driver.get(url)

    time.sleep(2)  
    
    #wait and get rid of any popups
    handlePopUps(driver) 
    time.sleep(1)
    
    #fill out name
    findElementAndSendKey(driver,nameFields,'JJ')
    time.sleep(1)   
    
    #fill out email
    findElementAndSendKey(driver,emailFields,'bumper1@gmail.com')
    time.sleep(1)  
    
    #find subject 
    subject = locate_with().below()
    #find_element(By.XPATH, "//input[following-sibling::input[@type='email']]")
    subject.send_keys('asdfsfasdfasd')
    print('found subject')
    #fill out Message
    findElementAndSendKey(driver,messageFields,'Hi there I like your beer')
    time.sleep(1)

    #click submit button
    findElementAndSendKey(driver,submitFields,None)
    found = False
    i = 0 
  
  
   
    time.sleep(4)
    driver.quit()
    
    
    

def getCompanyNameAndEmail(url):
    # listOfCompaniesInfoSites = getListOfCompanies()
    # url = 'https://www.coloradobrewerylist.com/brewery/baere-brewing-company/'
    companyWebsite = getWebsite(url)
    
    if companyWebsite is None: 
        return None, None
    if "http" not in companyWebsite:
        companyWebsite = "https://"+companyWebsite
    if companyWebsite[-1] != '/':
        companyWebsite = companyWebsite + '/'
    # print('website: '+companyWebsite) 
    companyName = getCompanyName(url)
    # print(companyName)
    emails = getEmail(companyWebsite)
    return companyName, emails
    
    

if __name__ == '__main__':
    # url = 'https://brewzonerifle.com/?fbclid=IwAR2EuqlXgVe32TKhh4G6PGMmeSmC8AFDn6nCq0H7ejNoh1eqDfLlNYmAKJc'
    url = 'https://www.cohesionbeer.com/contact'
    # url = 'https://www.selenium.dev/selenium/web/web-form.html'
    seleniumFillOutContactForm(url)