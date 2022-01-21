from .actions import chrome_driver, send_connection_request, linkedinProfiles, correct_job_title, \
    scrapEmpsData, extractValidEmails, exportData, getSheetData, demo, companies_info
from .constants import COOKIES
from .find_valid_email import find_users_valid_email


def start_bot():
    # driver = chrome_driver()
    #
    # driver.get("https://www.linkedin.com")
    # for cookie in COOKIES['deependra']:
    #     driver.add_cookie(cookie)
    #
    # driver.get("https://www.linkedin.com")
    # linkedinProfiles(driver, "Default Jobs Scrapper", "Android-India-All", 14)
    # linkedinProfiles(driver, "Default Jobs Scrapper", "Python-India-All", 14)
    # linkedinProfiles(driver, "Default Jobs Scrapper", "React Js-India-WeWorkRemotely", 14)
    # linkedinProfiles(driver, "Default Jobs Scrapper", "React Js-India-RemoteOk", 14)
    # linkedinProfiles(driver, "Default Jobs Scrapper", "Django-India-All", 14)
    # linkedinProfiles(driver, "Linkedin Jobs Scrapper", "Linkedin-jobs-Reactjs", 5)
    # linkedinProfiles(driver, "Linkedin Jobs Scrapper", "Django", 5)
    # linkedinProfiles(driver, "Linkedin Jobs Scrapper", "JavaScript", 5)
    # companies_info(driver, "Sourcing Research Worksheet", "Agencies")
    # scrapEmpsData(driver, False)
    # find_users_valid_email(["Django"])
    exportData("Prospects 2", "17th Jan")
    # driver.close()


start_bot()

# from scrapData import main
