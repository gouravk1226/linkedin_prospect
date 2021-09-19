from .actions import chrome_driver, send_connection_request, linkedinProfiles, correct_job_title, \
    scrapEmpsData, extractValidEmails, exportData, getSheetData
from .constants import COOKIES


def start_bot():
    driver = chrome_driver()

    driver.get("https://www.linkedin.com")
    for cookie in COOKIES['website_design']:
        driver.add_cookie(cookie)

    driver.get("https://www.linkedin.com")
    # send_connection_request(driver, "Linkedin Requests", "Sheet1", 20)
    # correct_job_title(driver, "Job Portals Data", "Android-Linkedin-India")

    linkedinProfiles(driver, "GoodFirm Companies Outside India", "Java", 8)
    scrapEmpsData(driver)
    # extractValidEmails()
    # exportData("Bowstring Data Scraping - Automation Sheet", "Marketing Companies Linkedin ")
    # getSheetData("Job Portals Data", "Android-India", 6)
    driver.close()


start_bot()
