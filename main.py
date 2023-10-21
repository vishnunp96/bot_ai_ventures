import sys
from typing import Tuple
from time import sleep
from datetime import time, datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from joblib import Parallel, delayed

# params
booking_site_url = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
begin_time = time(0, 0)
end_time = time(0, 15)
max_try = 500
# reservation_time and reservation_name are given as arguments when python script runs
reservation_time = int(sys.argv[1])
reservation_name = sys.argv[2]

options = Options()
# comment out this line to see the process in chrome
options.add_argument('--headless')
driver = webdriver.Chrome(
    '/Users/my_name/dev/stranger_bot/driver/chromedriver',
    options=options
)

jst = timezone(timedelta(hours=+9), 'JST')


def check_current_time(begin_time: time, end_time: time) -> Tuple[time, bool]:
    '''
    Check current time is between 00:00 and 00:15. 
    Returns current time and if it is between begin and end time.
    '''
    dt_now = datetime.now(jst)
    current_time = time(dt_now.hour, dt_now.minute, dt_now.second)
    return current_time, (begin_time <= current_time) and (current_time < end_time)


def make_a_reservation(reservation_time: int, reservation_name: str) -> bool:
    '''
    Make a reservation for the given time and name at the booking site.
    Return the status if the reservation is made successfully or not.
    '''
    try:
        driver.get(booking_site_url)

        # go to next week's page
        driver.find_element_by_xpath('/html/body/div[1]/main/section/div[1]/div[3]/ul[2]/li[3]') \
            .click()

        # click the given reservation time's box
        sleep(0.5)
        elements = driver.find_elements_by_xpath('//*[@id="js-lane"]')
        elements[reservation_time - 10].click()

        # fill in the number of the party
        input_box = driver.find_element_by_id('lessonEntryPaxCnt')
        input_box.clear()
        input_box.send_keys('2')

        # press book button
        btn = driver.find_element_by_xpath('//*[@id="menuDetailForm"]/section/div/div[1]/button')
        btn.click()

        # fill out contact info
        contact_dict = {
            'a': [
                'dummy_family_name_1', 'dummy_first_name_2', 'ナナシ', 'ゴンベ',
                'my_email.com', 'my_email.com', '0000000000'
            ],
            'b': [
                'dummy_family_name_2', 'dummy_family_name_2', 'ナナシ', 'ゴンコ',
                'email.com', 'email.com', '1111111111'
            ]
        }

        fill_info = contact_dict[reservation_name]
        full_name = fill_info[0] + ' ' + fill_info[1]
        print(f'Getting reservation for {full_name}')

        if reservation_name not in ['k', 'r']:
            raise ValueError('reservation_name needs to be either "r" or "k"')

        for idx, info in enumerate(fill_info):
            driver.find_element_by_xpath(
                f'//*[@id="frontLessonBookingEditForm"]/section[2]/table/tbody/tr[{idx + 1}]/td/div/input') \
                .send_keys(info)

        # press submit buttom
        btn = driver.find_element_by_xpath('//*[@id="frontLessonBookingEditForm"]/div[1]/button')
        btn.click()

        # press book button
        driver.find_element_by_id('btnBookingComplete').click()

        return True
    except Exception as e:
        print(e)
        return False
    finally:
        # close the drivers
        driver.quit()


def try_booking(reservation_time: int, reservation_name: str, max_try: int = 1000) -> None:
    '''
    Try booking a reservation until either one reservation is made successfully or the attempt time reaches the max_try
    '''
    # initialize the params
    current_time, is_during_running_time = check_current_time(begin_time, end_time)
    reservation_completed = False
    try_num = 1

    # repreat booking a reservation every second
    while True:
        if not is_during_running_time:
            print(f'Not Running the program. It is {current_time} and not between {begin_time} and {end_time}')

            # sleep less as the time gets close to the begin_time
            if current_time >= time(23, 59, 59):
                sleep(0.001)
            elif time(23, 59, 58) <= current_time < time(23, 59, 59):
                sleep(0.5)
            else:
                sleep(1)

            try_num += 1
            current_time, is_during_running_time = check_current_time(begin_time, end_time)
            continue

        print(f'----- try : {try_num} -----')
        # try to get ticket
        reservation_completed = make_a_reservation(reservation_time, reservation_name)

        if reservation_completed:
            print('Got a ticket!!')
            break
        elif try_num == max_try:
            print(f'Tried {try_num} times, but couldn\'t get tickets..')
            break
        else:
            sleep(1)
            try_num += 1
            current_time, is_during_running_time = check_current_time(begin_time, end_time)


if __name__ == '__main__':
    try_booking(reservation_time, reservation_name, max_try)