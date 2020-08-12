from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from getpass import getpass
import time

DRIVER_PATH="/Users/raghavvashisht/Downloads/chromedriver"

welcome_message = """

////////  Welcome to better-LMS-bennett-downloader build by dramikei //////// 

ABOUT: better-LMS-bennett-downloader lets you download the files/docs 
uploaded on Bennett student's LMS of either All or a particular subject.
If you face any problems or have an enhancement in mind, 
feel free to contact the developer or raise an issue 
or a PR at 
www.github.com/dramikei

"""
print(welcome_message)


USERNAME = input("Enter your LMS username: ")
PASSWORD = getpass("Enter your LMS password: ")

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_argument('--allow-running-insecure-content')
options.add_argument('--ignore-certificate-errors')

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

# Open LMS
driver.get("https://lms.bennett.edu.in/login/index.php") # TODO: Error handling

# Enter Student credentials
username = driver.find_element_by_xpath("//*[@id='username']").send_keys(USERNAME)
password = driver.find_element_by_xpath("//*[@id='password']").send_keys(PASSWORD)
submit = driver.find_element_by_xpath("//*[@id='loginbtn']").click()
# TODO: Error Handling

# TODO:
#Click on courses
# Store Courses and href in a dict.
# Print courses
#Iterate through courses
    #Open courses
    #download course contents
#GOTO Page 2
#REPEAT
time.sleep(2)
driver.save_screenshot('screenshot.png')

# print(driver.page_source)
driver.quit()

