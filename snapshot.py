from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome('/Users/mzhu1/Desktop/ubd-tool-remotedb/chromedriver', options=option)

driver.get('http://flood.umd.edu')
sleep(1)

count = 2
name = "app" + str(count) + ".png"

driver.get_screenshot_as_file('static/' + name)
driver.close()
driver.quit()
print("done!")



# how to make the website not pop up? 