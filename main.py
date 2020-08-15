from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from getpass import getpass
from urllib.parse import unquote
import requests
import time


DRIVER_PATH="/Users/raghavvashisht/Downloads/chromedriver"

welcome_message = """

////////  Welcome to better-LMS-bennett-downloader by dramikei //////// 

ABOUT: better-LMS-bennett-downloader lets you download the files/docs 
uploaded on Bennett student's LMS of either All or a particular subject.
If you face any problems or have an enhancement in mind, 
feel free to contact the developer or raise an issue 
or a PR at 
www.github.com/dramikei

"""
print(welcome_message)
COURSES = {}
TO_DOWN = []


USERNAME = input("Enter your LMS username: ")
PASSWORD = getpass("Enter your LMS password: ")
print("Please wait ...")

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_argument('--allow-running-insecure-content')
options.add_argument('--ignore-certificate-errors')

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

# To Supress warnings due to not verifying SSL certificate while using requests
requests.urllib3.disable_warnings()


def main():
    # Open LMS
    driver.get("https://lms.bennett.edu.in/login/index.php") # TODO: Error handling

    # Enter Student credentials
    username = driver.find_element_by_xpath("//*[@id='username']").send_keys(USERNAME)
    password = driver.find_element_by_xpath("//*[@id='password']").send_keys(PASSWORD)
    submit = driver.find_element_by_xpath("//*[@id='loginbtn']").click()
    # TODO: Error Handling

    # TODO:
    #Click on courses
    # driver.find_element_by_xpath("//*[@id='block-myoverview-view-choices-5f3401db5889f5f3401db588dc1']/li[2]/a").click()

    # Store Courses and href in COURSES dict
    find_courses()

    # Print courses
    print_courses()

    #Iterate through courses and download
    iterate_courses()
    #GOTO Page 2
    #REPEAT
    # time.sleep(2)
    # driver.save_screenshot('screenshot.png')

    # print(driver.page_source)
    driver.quit()

def find_courses():
    courses_div = driver.find_element_by_xpath("//*[@id='pc-for-in-progress']/div")
    anchors = courses_div.find_elements_by_tag_name("a")
    for elem in anchors:
        if elem.get_attribute("href") is not None:
            if "course/view.php?id=" in elem.get_attribute("href"):
                # print(elem.get_attribute("href"))
                COURSES[elem.text] = elem.get_attribute("href")

def print_courses():
    print("\n.\n.\n\nFound the following courses:\n")
    keys = list(COURSES.keys())
    index = 1
    for x in keys:
        print("{}) {}".format(index,x))
        index += 1
    print("\nWhose files do you want to download? \n(Enter single index, eg. 1 or a range, eg 0 - {} or A for ALL)\n".format(len(keys)))
    selection = input("Input selection: ")
    if selection == "A" or selection == "a":
        TO_DOWN.extend(keys)
    elif "-" in selection:
        selection_split = selection.split("-")
        starting = selection_split[0] if selection_split[0] < selection_split[1] else selection_split[1]
        ending = selection_split[0] if selection_split[0] > selection_split[1] else selection_split[1]
        for x in range(int(starting), int(ending)+1):
            TO_DOWN.append(keys[x])
    else:
        TO_DOWN.append(keys[int(selection)-1])
    print()
    print()
    print("////////////////////")

def iterate_courses():
    for key in TO_DOWN:
        # Open Course
        print("Opening course: {}\n".format(key))
        driver.find_element_by_link_text(key).click()

        # Download files from course
        print("Starting download from: {}\n".format(key))
        download()

        # Go back to courses page
        driver.back()


def download():
    #TODO: Implement
    div = driver.find_elements_by_class_name("activityinstance")
    for elem in div:
        resource = elem.find_element_by_tag_name("a")
        if resource.get_attribute("href") is not None:
            if "mod/resource/view.php?id=" in resource.get_attribute("href"):
                url = resource.get_attribute("href")
                agent = driver.execute_script("return navigator.userAgent")
                headers = {"User-Agent":agent}
                s = requests.session()
                s.headers.update(headers)
                #passing the cookies generated from the browser to the session
                for cookie in driver.get_cookies():
                    c = {cookie['name']: cookie['value']}
                    s.cookies.update(c)
                # Actually downlaod from Redirected-URL
                r = s.get(url, allow_redirects=True, verify=False)

                # Extract filename from Redirected-URL
                file_name = unquote(r.url.split('/')[-1])
                # file_name = file_name.replace("%20","_")
                print("Successfully Downloaded: ",file_name)
                with open(file_name, 'wb') as local_file:
                    local_file.write(r.content)

                    


if __name__=="__main__":
    main()