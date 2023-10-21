import sys
from time import sleep
from datetime import time, datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# params
booking_site_url = 'infosys.doc.ic.ac.uk/internalreg/'
registration_level_ai = 3

max_try = 2000
max_error = 10

time_interval = int(sys.argv[1])
username = sys.argv[2]
pwd = sys.argv[3]

options = Options()
# comment out this line to see the process in chrome
# options.add_argument('--headless')
options.add_argument('--incognito')
driver = webdriver.Chrome(
    # '/Users/my_name/dev/stranger_bot/driver/chromedriver',
    options=options
)

def make_a_reservation(username: str, pwd: str) -> bool:
    '''
    Load the website with basic authentication, passing PLAIN TEXT username and password.
    If button found, update is attempted.
    '''
    try:
        driver.get("https://" + username + ":" + pwd + "@" + booking_site_url)

        sleep(0.5)

        table_courses = driver.find_elements(By.XPATH, "/html/body/form/table")[0]
        found_req_row = False
        button_clicked = False
        for index, row in enumerate(table_courses.find_elements(By.TAG_NAME, "tr")):
            for colindex,col in enumerate(row.find_elements(By.TAG_NAME, "td")):
                if("AI Ventures" in col.text):
                    # print("found it here at least,", colindex)
                    found_req_row = True
                if(found_req_row and colindex == 7 + registration_level_ai):
                    try:
                        col.find_elements(By.TAG_NAME, "input")[0].click()
                        button_clicked = True
                    except IndexError as ie:
                        button_clicked = False
                        print("AI Ventures is not open yet..")
                    except Exception as e:
                        button_clicked = False
                        print("Button clicking had some problem:", e)

            if(found_req_row):
                break

        if(found_req_row and button_clicked):
            try:
                update_row = table_courses.find_elements(By.TAG_NAME, "tr")[-1]
                update_col = update_row.find_elements(By.TAG_NAME, "td")[-1]
                for update_button in update_col.find_elements(By.TAG_NAME, "input"):
                    if("Submit" in update_button.accessible_name):
                        update_button.click()
                        break
            except Exception as e:
                button_clicked = False
                print("There was some issue with the update button:", e)

        if(found_req_row and button_clicked):
            return True
    except Exception as e:
        raise e
    finally:
        return False


def try_booking(time_interval: int, username: str, pwd: str, max_try: int = 1000) -> None:
    '''
    Keep trying until max_try with interval of time_interval to go through with the booking.
    If max_errors hit, back off for 10*time_interval minutes before continuing
    '''
    reservation_completed = False
    try_num = 1
    num_error = 0

    # repeat booking a reservation every time_interval minutes
    while True:

        print(f'----- try : {try_num} -----')
        # try to get ticket
        try:
            reservation_completed = make_a_reservation(username, pwd)
        except Exception as none:
            num_error += 1

        if reservation_completed:
            print('Got AI venture!!')
            break
        elif try_num == max_try:
            print(f'Tried {try_num} times, but couldn\'t get AI venture..')
            break
        elif num_error >= max_error:
            print('Too many errors, better to back off for a bit.. ')
            sleep(time_interval*10*60)
            num_error = 0
        else:
            print("Current time :\t", datetime.now())
            print("Next try:\t", datetime.now() + timedelta(minutes=time_interval))
            sleep(time_interval*60)
            try_num += 1

    driver.quit()


if __name__ == '__main__':
    try_booking(time_interval, username, pwd, max_try)