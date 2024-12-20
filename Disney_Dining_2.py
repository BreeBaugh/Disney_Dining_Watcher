################# IMPORTS ##################
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime
import requests
import json
from getpass import getpass
import twilio
from twilio.rest import Client
############################################



##################### Description #####################
#This program was built prior to traveling to California in January 2021.
#During the trip, plans were made to visit the Disney parks in Anaheim.
#This program was made to scrub Disney's dining reservation site and
#send me (the end-user) texts when reservations spots to restaurants of
#of interest were available. It also provided me a link to the reservation
#page so the reservation could be made hastily.
########################################################




# Path to the chrome web driver
# s = Service('C:\Program Files (x86)\chromedriver.exe')
# driver = webdriver.Chrome(service=s)
chrome_options=Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://disneyland.disney.go.com/dining/#/reservations-accepted/")



driver.implicitly_wait(10)

def main():
    go = True
    userInput = ""
    while go is True:
        findRestaurant()

def findRestaurant():
    q = 0
    z = 0


    while q < 3:
        calander = driver.find_element(By.ID, "diningAvailabilityForm-searchDate")
        calander.click()
        calander.clear()
        calander.send_keys("01/04/2022")

        timeSelect = driver.find_element(By.ID, "diningAvailabilityForm-searchTimeid-base")
        timeSelect.click()

        timeSearch = driver.find_element(By.ID, "diningAvailabilityForm-searchTime-" + str(q))
        timeSearch.click()

        driver.find_element(By.ID, "dineAvailSearchButton").click()
        #Calls the restaurant availibility function
        restaurantAvailability()
        q += 1

    while z < 3:
        calander = driver.find_element(By.ID, "diningAvailabilityForm-searchDate")
        calander.click()
        calander.clear()
        calander.send_keys("01/05/2022")

        timeSelect = driver.find_element(By.ID, "diningAvailabilityForm-searchTimeid-base")
        timeSelect.click()

        timeSearch = driver.find_element(By.ID, "diningAvailabilityForm-searchTime-" + str(z))
        timeSearch.click()

        driver.find_element(By.ID, "dineAvailSearchButton").click()
        #Calls the restaurant availibility function
        restaurantAvailability()
        z += 1


# = driver.find_element(By.ID, "noAvailability-alpha-default")

#BBID = "354099;entityType=restaurant"
#blueBayou = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[5]/div[1]/div/div[4]/section/div/ul[2]/li[2]/div[1]/div[1]/div/div[2]/span[1]").text

def restaurantAvailability():
    restarantsList = ["Blue Bayou Restaurant", "Cafe Orleans", "Carthay Circle Restaurant", "Oga's Cantina at the Disneyland Resort"]
    availableList = []
    lastList = []

    for x in range(0,5):
        # print(x)
        # print("RL", len(restarantsList))
        restarants = driver.find_elements(By.CSS_SELECTOR, ".card.dining.show")
        for restaurant in restarants:
            name = restaurant.find_element(By.CSS_SELECTOR, ".cardName").text
            if name in restarantsList:
                print(name)
                restarantsList.remove(name)
                try:
                    times = restaurant.find_elements(By.CSS_SELECTOR, "[data-servicedatetime]")
                    if len(times) > 0:
                        print("available")
                        availableList.append(name)
                        for time in times:
                            print(time.get_attribute("data-servicedatetime")[11:-9])
                            timeFound = time.get_attribute("data-servicedatetime")[11:-9]
                            availableList.append(timeFound)
                        availableList.append("-")

                    else:
                        print("Unavailable")
                except:
                    print("Unavailable")
                break
    if len(availableList) > 2:
        smsSend = ""
        for v in availableList:
            smsSend += v + " "

        textMe(smsSend)

#The TextMe Function used to text me when times are found.

# Find these values at https://twilio.com/user/account
# To set up environmental variables, see http://twil.io/secure


#Admittidly NOT a safe or secure way to handle authentication for texting API,
#but this was built hastily right before a trip, and also I wasn't
#as well versed with security measures when this was built

account_sid = ''     #Account sid goes here
auth_token = ''      #Auth token goes here

def textMe(message):
    client = Client(account_sid, auth_token)

    client.api.account.messages.create(
        to="", #Phone Number as String
        from_="", #Phone Number as String
        body=message)



main()
