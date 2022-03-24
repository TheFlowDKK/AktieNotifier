from cgitb import text
from time import sleep
from bs4 import BeautifulSoup
import os
import requests
from pushnotifier import PushNotifier as pn
from dotenv import load_dotenv

with open("config", "r") as f:
    lines = f.readlines()
    stock = lines[1].strip().split(",")
    sleepTime = float(lines[4].strip())
    baseURL = "https://www.nordnet.dk/markedet/aktiekurser/"
    stockRaise = float(lines[7].strip())
    stockDrop = float(lines[10].strip())

print("Config file loaded...")

load_dotenv()
name = os.getenv('name')
password = os.getenv('password')
package = os.getenv('package')
token = os.getenv('token')

pn = pn.PushNotifier(name, password, package, token)
pn.login(password)

global percent
percent = []

def sendMessage(message):
    sent = False
    while sent == False:
        if pn.send_text(message) == 200:
            print("Sendte besked")
            sent = True
        else:
            print("Kunne ikke sende besked.")
            sleep(5)

def scrape(stock):
    with requests.Session() as s:
        html = BeautifulSoup(s.get(baseURL + stock).content, "html.parser").find("span", class_="Typography__Span-sc-10mju41-0 gaHPGY Typography__StyledTypography-sc-10mju41-1 epuleM StatsBox__StyledPriceText-sc-163f223-2 djnBAa").getText()
        html = html.split(",")
        html = '.'.join(html)
        return float(html)

def checkPercent(lastPercent, currentPercent, min, max, stock, number):
    if currentPercent >= lastPercent + max:
        percent[number] = currentPercent
        sendMessage(stock + " er steget med " + str(currentPercent-lastPercent) + "%")
        print("Stigning: " + stock + " " + str(currentPercent-lastPercent) + "%")
    elif currentPercent <= lastPercent - min:
        percent[number] = currentPercent
        sendMessage(stock + " er faldet med " + str(lastPercent-currentPercent) + "%")
        print("Fald: " + stock + " " + str(lastPercent-currentPercent) + "%")
    return


if __name__ == "__main__":
    for i in range(len(stock)):
        percent.append(scrape(stock[i]))

    while True:
        for i in range(len(stock)):
            checkPercent(percent[i], scrape(stock[i]), stockDrop, stockRaise, stock[i], i)
        sleep(sleepTime)
