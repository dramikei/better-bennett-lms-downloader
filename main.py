from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from getpass import getpass
from urllib.parse import unquote
import os
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

download_choice = -1
iterating_past = False
current_page = 1
pages = 1

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
    print("Do you want to download Present course, past or both?")
    print("1: Present")
    print("2: Past")
    print("3: Both")
    
    global download_choice
    global iterating_past
    global current_page
    global pages
    
    download_choice = int(input("Enter: "))
    
    if download_choice != 1 and download_choice != 2 and download_choice != 3:
        print("Wrong choice!")
    elif download_choice == 2:
        gotoPast()
        iterating_past = True
        # time.sleep(2)
    elif download_choice == 3:
        pages = 2
    
    for _ in range(0, pages):
        # Pages (1/2/3) in current Section (Present/Past)
        if iterating_past:
            html_list = driver.find_element_by_xpath("//*[@id='pb-for-past']/ul")
        else:
            html_list = driver.find_element_by_xpath("//*[@id='pb-for-in-progress']/ul")
        items = html_list.find_elements_by_tag_name("li")
        
        # Go through every page and downlaod
        for i in range(1,len(items) - 1):
            COURSES.clear()
            TO_DOWN.clear()
            # Store Courses and href in COURSES dict
            find_courses()

            # # Print courses
            print_courses()

            # #Iterate through courses and download
            iterate_courses()
            # driver.save_screenshot(str(i)+'screenshot.png')
            if i != len(items) - 2:
                if iterating_past:
                    html_list = driver.find_element_by_xpath("//*[@id='pb-for-past']/ul")
                else:
                    html_list = driver.find_element_by_xpath("//*[@id='pb-for-in-progress']/ul")
                print("Going to page:",(i+1))
                html_list.find_element_by_partial_link_text(str(i+1)).click()
                current_page = i+1
                time.sleep(0.5)
    
    # GOTO Past
    if pages == 2:
        gotoPast()
        iterating_past = True

    #REPEAT
    # time.sleep(2)
    # driver.save_screenshot('screenshot.png')

    # print(driver.page_source)

    driver.quit()

def find_courses():
    time.sleep(1)
    global COURSES
    main_dov = None
    if iterating_past:
        main_div = driver.find_element_by_xpath("//*[@id='myoverview_courses_view_past']")
    else:
        main_div = driver.find_element_by_xpath("//*[@id='myoverview_courses_view_in_progress']")
    courses_div = main_div.find_element_by_xpath(".//*[@id='pc-for-in-progress']") 
    anchors = courses_div.find_elements_by_tag_name("a")
    for elem in anchors:
        if elem.get_attribute("href") is not None:
            if "course/view.php?id=" in elem.get_attribute("href") and elem.text != '':
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
            TO_DOWN.append(keys[x-1])
    else:
        TO_DOWN.append(keys[int(selection)-1])
    print()
    print()
    print("////////////////////")

def iterate_courses():
    for key in TO_DOWN:
        time.sleep(1)
        # Open Course
        print("Opening course: {}\n".format(key))
        driver.find_element_by_link_text(key).click()

        # Download files from course
        print("Starting download from: {}\n".format(key))
        download(key)

        # Go back to courses page
        global iterating_past
        if iterating_past:
            driver.back()
            time.sleep(0.5)
            gotoPast()
        time.sleep(0.5)
        gotoPage()


def download(course_name):
    time.sleep(1)
    course_name = course_name.replace(":","-")
    download_path = os.getcwd()+"/downloads"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    course_path = download_path+"/{}".format(course_name)
    print(course_path)
    print(course_name)
    if not os.path.exists(course_path):
        os.mkdir(course_path)
    
    # Prepare to use Requests
    agent = driver.execute_script("return navigator.userAgent")
    s = requests.session()

    # Passing the header from Selenium to Requests session
    s.headers.update({"User-Agent":agent})

    # Passing the cookies generated from the browser to the session
    for cookie in driver.get_cookies():
        s.cookies.update({cookie['name']: cookie['value']})
    
    # Find files to download
    div = driver.find_elements_by_class_name("activityinstance")
    for elem in div:
        resource = elem.find_element_by_tag_name("a")
        if resource.get_attribute("href") is not None:
            # Find file's URL
            if "mod/resource/view.php?id=" in resource.get_attribute("href"):
                url = resource.get_attribute("href")

                # Actually downlaod from Redirected-URL using the Requests session
                r = s.get(url, allow_redirects=True, verify=False)

                # Extract filename from Redirected-URL
                file_name = unquote(r.url.split('/')[-1])
                # file_name = file_name.replace("%20","_")
                print("Downloaded: ",file_name)
                # Save File.
                with open(course_path+"/"+file_name, 'wb') as local_file:
                    local_file.write(r.content)

                    
def gotoPast():
    driver.find_element_by_link_text("Past").click()
def gotoPage():
    if current_page != 1:
        if iterating_past:
            html_list = driver.find_element_by_xpath("//*[@id='pb-for-past']/ul")
        else:
            html_list = driver.find_element_by_xpath("//*[@id='pb-for-in-progress']/ul")
        
        html_list.find_element_by_partial_link_text(str(current_page)).click()

if __name__=="__main__":
    main()