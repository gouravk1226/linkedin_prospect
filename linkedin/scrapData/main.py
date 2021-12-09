from .actions import chrome_driver, send_connection_request, linkedinProfiles, correct_job_title, \
    scrapEmpsData, extractValidEmails, exportData, getSheetData, demo
from .constants import COOKIES


def start_bot():
    # driver = chrome_driver()
    #
    # driver.get("https://www.linkedin.com")
    # for cookie in COOKIES['sahil']:
    #     driver.add_cookie(cookie)
    #
    # driver.get("https://www.linkedin.com")

    # linkedinProfiles(driver, "Sourcing Research Worksheet", "Agencies", 12)
    # scrapEmpsData(driver)
    exportData("Prospects", "react js")
    # driver.close()


start_bot()

# from scrapData import main
