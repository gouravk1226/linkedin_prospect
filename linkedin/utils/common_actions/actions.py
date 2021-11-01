import time
from selenium import webdriver
from datetime import datetime
import pytz
from utils.common_constants.constants import BRIDGEFIX_SCRAPPER_SHEET_CN


def wait(t):
    time.sleep(t)


def chrome_driver():

    driver_location = "/usr/bin/chromedriver"
    binary_location = "/usr/bin/google-chrome"

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = binary_location
    web_driver = webdriver.Chrome(executable_path=driver_location, chrome_options=options)
    web_driver.maximize_window()
    web_driver.implicitly_wait(10)
    return web_driver


def current_time():
    tz_NY = pytz.timezone('Asia/Kolkata')
    datetime_NY = datetime.now(tz_NY)
    dt_string = datetime_NY.strftime("%Y-%m-%d %H:%M:%S.%f").split(".")[0]

    return dt_string


def match_column(column_name, matched_with, columns, i):
    if column_name.lower() == matched_with.lower():
        columns.update({
            column_name: i,
        })


def find_column_numbers(data):
    columns = {}
    i = 1
    for column_name in data.keys():
        match_column(column_name, BRIDGEFIX_SCRAPPER_SHEET_CN['sheet_name'], columns, i)
        match_column(column_name, BRIDGEFIX_SCRAPPER_SHEET_CN['tab_name'], columns, i)
        match_column(column_name, BRIDGEFIX_SCRAPPER_SHEET_CN['keyword'], columns, i)
        match_column(column_name, BRIDGEFIX_SCRAPPER_SHEET_CN['url'], columns, i)
        match_column(column_name, BRIDGEFIX_SCRAPPER_SHEET_CN['scrapping_start'], columns, i)
        match_column(column_name, BRIDGEFIX_SCRAPPER_SHEET_CN['scrapping_complete'], columns, i)

        i += 1

    return columns

