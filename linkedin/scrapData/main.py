from .actions import chrome_driver, send_connection_request, linkedinProfiles, correct_job_title, \
    scrapEmpsData, extractValidEmails, exportData, getSheetData, demo
from .constants import COOKIES


def start_bot():
    driver = chrome_driver()

    driver.get("https://www.linkedin.com")
    for cookie in COOKIES['website_design']:
        driver.add_cookie(cookie)

    driver.get("https://www.linkedin.com")

    # send_connection_request(driver, "Linkedin Requests", "Sheet1", 20)
    # correct_job_title(driver, "Job Portals Data", "Android-Linkedin-India")

    # linkedinProfiles(driver, "Monster1", "wordpress developer", 9)
    # linkedinProfiles(driver, "Monster1", "React developer", 9)
    # linkedinProfiles(driver, "Monster1", "Sales and marketing", 9)
    # linkedinProfiles(driver, "Monster1", "Android developer", 9)
    # linkedinProfiles(driver, "Monster1", "Django developer", 9)
    # linkedinProfiles(driver, "Default Data - Automation Scrapper", "Input - Android Data", 4)
    scrapEmpsData(driver)
    # extractValidEmails()
    # exportData("Goodfirms Data", "D-React-Software Development-LI-Users")
    # exportData("Goodfirms Data", "BSS - Wordpress - LI - Users")
    # getSheetData("GoodFirm Companies Outside India", "Service Web US", 7)
    driver.close()


start_bot()
