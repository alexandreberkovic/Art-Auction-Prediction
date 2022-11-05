# # Scrapping algorithm to extract sleeping information from Withings plateform

# ## Imports

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
import datetime as dt
import time
import requests
import pandas as pd
import time


# ## Chrome driver initialization


options = ChromeOptions()
options.add_argument("--start-maximized")
# initialize the Chrome driver
driver = webdriver.Chrome("chromedriver",options=options)
driver.maximize_window()


def login():
    # head to Withings login page
    driver.get("https://account.withings.com/connectionwou/account_login?r=https://healthmate.withings.com/")
    # Withings credentials
    username = "ab10718@ic.ac.uk"
    password = "DE4IoT!"

    # ## Reaching the data
    # accept cookies
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//*[@class='accept-all primary']")))[0].click()
    time.sleep(2)
    # find username/email field and send the username itself to the input field
    driver.find_element_by_name('email').send_keys(username)
    # find password input field and insert password as well
    driver.find_element_by_name('password').send_keys(password)
    # click login button
    driver.find_element_by_class_name("primary").click()

    # wait the ready state to be complete
    WebDriverWait(driver=driver, timeout=10).until(
        lambda x: x.execute_script("return document.readyState === 'complete'"))
    error_message = "Incorrect username or password."
    # get the errors (if there are)
    errors = driver.find_elements_by_class_name("flash-error")
    # if we find that error message within errors, then login is failed
    if any(error_message in e.text for e in errors):
        print("[!] Login failed")
    else:
        print("[+] Login successful")

def sleep_data():
    # ### Reach the sleeping data page
    # WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//*[@class='item self-activity-sleep sleep']")))[0].click()
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div/div[1]/ul/li[3]/div")))[0].click()
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//*[@class='HMIcons_close action js-close']")))[0].click()
    string = '//*[@id="sleep-content"]/div/div[2]/ul/li[1]/div/div[1]/div[1]/p'
    time.sleep(2)
    # string.split('li[1]')

    # change li number to get the date
    elem = driver.find_element_by_xpath('//*[@id="sleep-content"]/div/div[2]/ul/li[1]/div/div[1]/div[1]/p')
    # elem.text
    element = driver.find_element_by_xpath("//li[1]//*[contains(@class, 'content')]//*[contains(@class, 'blocl')]//*[contains(@class, 'graph')]//*[name()='svg']//*[name()='g']//*[name()='rect' and contains(@class, 'shadow-rect')]")
    hover = ActionChains(driver).move_to_element(element)
    hover.perform()

def get_data(date,main,sub,li,driver):
    lst = []
    for i in range(1,li):
        dateStr = date.split('li[1]')
        elem = driver.find_element_by_xpath(dateStr[0]+'li['+str(i)+']'+dateStr[1])
        dateFinal = elem.text.split('(Sleep)')[0]
        charts = main.split('li[1]')
        newMain = str(charts[0]+'li['+str(i)+']'+charts[1]) 
        links = driver.find_elements_by_xpath(newMain)
        for values in links:
            hover = ActionChains(driver).move_to_element(values)
            hover.perform()
            subStr = driver.find_element_by_xpath(sub)
            sleep = subStr.text
            sleep = sleep.split(',')
            lst.append([dateFinal,sleep[0],sleep[1]])
        if i%10==0:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # time.sleep(2)
    return lst
    
    
def dataframe(data):
    #Léger, Profond, Reveillé, Paradoxal
    dfs = pd.DataFrame(data, columns = ['Date','Pattern','Time'])

    for i in range(len(dfs)):
        if dfs['Pattern'][i] == 'Reveillé':
            dfs['Pattern'][i] = 'Awake'
        elif dfs['Pattern'][i] == 'Léger':
            dfs['Pattern'][i] = 'Light'
        elif dfs['Pattern'][i] == 'Profond':
            dfs['Pattern'][i] = 'Deep'
        elif dfs['Pattern'][i] == 'Paradoxal':
            dfs['Pattern'][i] = 'REM'

    for i in range(len(dfs)):
        lst = dfs['Date'][i].split(' ')
        if lst[1] == 'novembre':
            dfs['Date'][i] = str(lst[0]+ ' ' + 'November' + ' ' +lst[2])
        elif lst[1] == 'décembre':
            dfs['Date'][i] = str(lst[0]+ ' ' + 'December' + ' ' +lst[2])

    return dfs

def main(): 
    date = '//*[@id="sleep-content"]/div/div[2]/ul/li[1]/div/div[1]/div[1]/p'
    main = "//li[1]//*[contains(@class, 'content')]//*[contains(@class, 'blocl')]//*[contains(@class, 'graph')]//*[name()='svg']//*[name()='g']//*[name()='rect' and contains(@class, 'shadow-rect')]"
    sub = "//*[local-name()='svg' and @height=235]//*[name()='g']//*[name()='text' and @class='tooltip-value']"
    d0 = pd.to_datetime('14/11/2021', format='%d/%m/%Y') # initial date
    d1 = pd.to_datetime("today")
    delta = d1 - d0
    li = delta.days #current date
    time.sleep(1)
    login()
    time.sleep(5)
    sleep_data()
    time.sleep(1)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)
    data = get_data(date,main,sub,li,driver)
    dfs = dataframe(data)
    dfs.to_csv('Scraping_data.csv')
        
if __name__ == "__main__":
    main()