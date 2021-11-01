from .constants import URLS, CSS_SELECTOR, IDS, CREDS, XPATHS
from selenium.webdriver.common.keys import Keys
from utils.common_actions.actions import wait
from utils.common_actions.actions import chrome_driver


def glassdoorLogin(driver):
    driver.get(URLS['login'])
    driver.find_element_by_css_selector(CSS_SELECTOR['sign_in_button']).click()
    wait(5)

    userEmail = driver.find_element_by_id(IDS['userEmail'])
    userPassword = driver.find_element_by_id(IDS['userPassword'])
    userEmail.send_keys(CREDS['email'])
    wait(1)

    userPassword.send_keys(CREDS['password'])
    userPassword.send_keys(Keys.ENTER)
    wait(2)

    return 0


def storeData(driver, tech):
    all_jobs = driver.find_elements_by_css_selector('li.css-bkasv9.eigr9kq0')
    for job in all_jobs:
        job_detail = job.text.splitlines()
        print(job_detail)
        if len(job_detail) == 6:
            company_name = job_detail[0]
            job_title = job_detail[1]
            job_location = job_detail[2]
            salary_detail = job_detail[3]

            print(company_name, job_title, job_location, salary_detail)


def nextPage(driver, target_page):
    for i in range(2, 7):
        page_object = driver.find_element_by_xpath(XPATHS['page_no'].format(i))
        page_no = int(page_object.text)
        if page_no == target_page:
            page_object.click()
            wait(3)
            return 0


def jobs(driver, url, tech):
    glassdoorLogin(driver)
    driver.get(url)
    total_pages = int(
        driver.find_element_by_css_selector('div.cell.middle.d-none.d-md-block.py-sm').text.split(" ")[-1])

    for i in range(total_pages):
        print("Page Number - {}".format(i))
        storeData(driver, tech)
        try:
            nextPage(driver, i)
        except:
            driver.find_element_by_css_selector('span.SVGInline.modal_closeIcon').click()
            nextPage(driver, i)

