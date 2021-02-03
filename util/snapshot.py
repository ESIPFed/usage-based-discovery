from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome('./chromedriver', options=option)

driver.get('https://disc.gsfc.nasa.gov/information/data-in-action?title=Cyclone%20Harold%20Tracks%20Through%20Idyllic%20Islands%20of%20the%20South%20Pacific')
sleep(1)

count = 2
name = "test.png"
# name = "app" + str(count) + ".png"

driver.get_screenshot_as_file('static/' + name)
driver.close()
driver.quit()



# how to make the website not pop up? 
