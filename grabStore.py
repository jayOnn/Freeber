from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from chromedriver_py import binary_path  # Adds chromedriver binary to path
import csv
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=binary_path)
driver.get("https://www.ubereats.com/ca")

#script variables
delay = 5 # seconds
curLocal ="Toronto, Ontario"
curTS = time.time()
countFreeItems = 0

#output 
storeListFile = "Store."+curLocal+"."+str(curTS)+".file"
customList = storeListFile+".custom"
csvFile = storeListFile + ".csv"
csvFields = ['Food Item', 'URL']

def goToLocation(location):
    locationInput = driver.find_element_by_id("location-typeahead-home-input")
    locationInput.send_keys(location)
    time.sleep(3)
    actions = ActionChains(driver)
    actions.send_keys(Keys.DOWN).perform()
    time.sleep(1)
    actions.send_keys(Keys.RETURN).perform()

def grabAllStorePage():
    restURLS = driver.find_elements(By.XPATH,'//a[contains(@href, "%s")]' % 'food-delivery')
    with open(storeListFile, "a+") as f:
        for items in restURLS:
            #print(items.get_attribute('href'))
            dupFlag = 0
            contents = f.read()
            for entry in contents.split('\n'):
                if entry == items.get_attribute('href'):
                    dupFlag = 1
                    break
            if dupFlag == 0:
                f.write(items.get_attribute('href')+'\n')
        f.close()
    print("Scrape nearby stores")

def findCustomDiv():
    print("Scanning for Food...")
    with open(storeListFile, "r") as f:
        with open(csvFile, "w+") as cf:
            csvwriter = csv.DictWriter(cf,fieldnames=csvFields)
            csvwriter.writeheader()
            contents = f.read()
            for link in contents.split('\n'):
                if(len(link) > 2):
                    driver.get(link)
                    try:
                        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//*[@id='main-content']")))
                        time.sleep(3)
                        items = driver.find_elements(By.CSS_SELECTOR,'ul.cb li div.bk.ag')
                        if(len(items) < 1):
                            items = driver.find_elements(By.CSS_SELECTOR,'ul.cb li div.c2.ag')
                        for it in items:
                            actions = ActionChains(driver)
                            actions.move_to_element(it).click(it).perform()
                            time.sleep(5)
                            #look for Button avaliable
                            activeButton = driver.find_elements(By.XPATH,'//div[@role="dialog"]/div/div/button') 
                            if(len(activeButton) > 0):
                                # print("bgcolor: "+activeButton[0].value_of_css_property("background-color"))
                                if(activeButton[0].value_of_css_property("background-color") != 'rgba(246, 246, 246, 1)'): 
                                    itemName = driver.find_element(By.XPATH,'//div[@role="dialog"]/div/div/h1').text
                                    csvwriter.writerow({'Food Item': itemName, 'URL': link})
                                    ++countFreeItems
                            # print(link+" - got free food")
                            else:
                                print("nothing here")
                            closeButton =  driver.find_element(By.XPATH,'//button[@aria-label="Close"]').click()
                    except TimeoutException:
                        print ("Error!")


try:
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'location-typeahead-home-input')))
    goToLocation(curLocal)
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'search-suggestions-typeahead-input')))
    time.sleep(5)
    grabAllStorePage()
    time.sleep(5)
    findCustomDiv()
    driver.close()
    print('Scan Complete. '+countFreeItems+' item(s) found')
except TimeoutException:
    print ("Error!")







    