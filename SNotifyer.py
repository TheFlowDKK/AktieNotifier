from time import sleep
from bs4 import BeautifulSoup
import os
import requests
from pushnotifier import PushNotifier as pn
from dotenv import load_dotenv
from datetime import datetime

with open("config", "r") as f:
    lines = f.readlines()
    stock = lines[1].strip().split(",")
    sleepTime = float(lines[4].strip())
    baseURL = "https://www.nordnet.dk/markedet/aktiekurser/"
    stockRaise = float(lines[7].strip())
    stockDrop = float(lines[10].strip())
    logStat = int(lines[13].strip())

print("Config file loaded...")


load_dotenv()
name = os.getenv('name')
password = os.getenv('password')
package = os.getenv('package')
token = os.getenv('token')

print(".env file loaded...")

pn = pn.PushNotifier(name, password, package, token)
pn.login(password)

print("Logged in to PushNotifier...")

global percent
percent = []

def sendMessage(message):
    sent = False
    while sent == False:
        if pn.send_text(message) == 200:
            write(log, "=== Sendte besked ===", datetime.now().strftime("%H:%M:%S"))
            sent = True
        else:
            write(log, "!!! Kunne ikke sende besked !!!", datetime.now().strftime("%H:%M:%S"))
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
        write(log, "+++ Stigning: " + stock + " " + str(currentPercent-lastPercent) + "% +++\n", datetime.now().strftime("%H:%M:%S"))
    elif currentPercent <= lastPercent - min:
        percent[number] = currentPercent
        sendMessage(stock + " er faldet med " + str(lastPercent-currentPercent) + "%")
        write(log, "--- Fald: " + stock + " " + str(lastPercent-currentPercent) + "% ---\n", datetime.now().strftime("%H:%M:%S"))
    else:
        write(log, "%%% Saved percentage " + stock + ": " + str(percent[number]) + " %%%", datetime.now().strftime("%H:%M:%S"))
        write(log, "%%% Current percentage " + stock + ": " + str(currentPercent) + " %%% \n", datetime.now().strftime("%H:%M:%S"))
    return

def write(log, message, time):
    if log == True:
        with open("log", "a") as f:
            f.write("[" + time + "] " + message + "\n")
    elif log == "Disabled":
        return
    else:
        log = True
        with open("log", "w") as f:
            f.write("[" + time + "] " + message + "\n")
    print("[" + time + "] " + message)
    return log


if __name__ == "__main__":
    if logStat == 1:
        print("Log started...")
        if os.path.exists("log"):
            log = True
        else:
            log = False
        log = write(log, "Log started", datetime.now().strftime("%H:%M:%S"))
    else:
        print("Log not started...")
        log = "Disabled"


    for i in range(len(stock)):
        percent.append(scrape(stock[i]))

    while True:
        for i in range(len(stock)):
            checkPercent(percent[i], scrape(stock[i]), stockDrop, stockRaise, stock[i], i)
        sleep(sleepTime)
