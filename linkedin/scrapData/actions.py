import random
from selenium import webdriver
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .constants import scope, CREDS_FILE_LOCATION, headers, CSS_SELECTOR, POSITIONS, XPATHS, CLASS_NAMES, SAAS_SHEET, \
    SAAS_TAB1, COOKIES, JOB_SHEET, TABS, message
import requests
from bs4 import BeautifulSoup
import time
from .models import Companies, UsersData
from verify_email import verify_email


def wait(t):
    time.sleep(t)


def random_wait(a, b):
    t = random.randint(a, b)
    wait(t)


def chrome_driver():
    driver_location = "/usr/bin/chromedriver"
    binary_location = "/usr/bin/google-chrome"

    options = webdriver.ChromeOptions()
    options.binary_location = binary_location
    web_driver = webdriver.Chrome(executable_path=driver_location, chrome_options=options)
    web_driver.maximize_window()
    web_driver.implicitly_wait(5)
    return web_driver


def google_sheet_client():
    """Will return client which we will use in other functions to open sheet"""
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE_LOCATION, scope)

    client = gspread.authorize(creds)

    return client


def sheet_data(sheet_name, tab_name):
    """Function will return sheet data and sheet instance so that we can update sheet from other functions"""
    client = google_sheet_client()

    sheet = client.open(sheet_name).worksheet(tab_name)

    data = sheet.get_all_records()

    return data, sheet


def findCompanyLinkedinUrl(soup):
    all_links = soup.find_all("a")

    for link in all_links:
        try:
            url = link['href']

            if "linkedin.com/company" in url:
                return url
        except:
            pass

    return "NA"


def getSheetData(sheet_name, tab_name, column_number):
    all_data, sheet = sheet_data(sheet_name, tab_name)

    row = 2
    for data in all_data:
        try:
            company_website = data['Website']
            linkedin_url = data['Company Linkedin']

            if not len(linkedin_url):
                response = requests.get("{}".format(company_website), headers)
                soup = BeautifulSoup(response.text, 'lxml')
                company_linkedin = findCompanyLinkedinUrl(soup)
                print(row, company_website, company_linkedin)
                sheet.update_cell(row, column_number, company_linkedin)

        except Exception as ex:
            print(ex)
        row += 1


def clickOnAllEmployees(driver):
    clicked = False

    try:
        emp = driver.find_element_by_css_selector(CSS_SELECTOR['employees'])
        emp.click()
        wait(5)
        print("Clicked")
        clicked = True

    except Exception as ex:
        # print(ex)
        pass

    return clicked


def randomWait(i, j):
    t = random.randint(i, j)
    wait(t)


def job_title(driver):
    position = "Not Found"
    try:
        for i in range(15):
            driver.execute_script(f"window.scrollTo(0, {i*100})")
            wait(0.1)
        driver.execute_script("window.scrollTo(0, 0)")
        for i in range(15):
            driver.execute_script(f"window.scrollTo(0, {i*100})")
            wait(0.1)
        experience = driver.find_element_by_css_selector('section.pv-profile-section.experience-section.ember-view').text.splitlines()
        position = experience[1]
        if position == "Company Name":
            position = experience[6]
    except Exception as ex:
        # print(ex)
        pass

    return position


def correct_job_title(driver, sheet_name, tab_name):
    all_data, sheet = sheet_data(sheet_name, tab_name)

    row = 2
    for data in all_data:
        print(row)
        title = data['Job Title']
        if title == "Not Found" or title == "Company Name":
            url = data['Linkedin Profile Url']
            driver.get(url)
            position = job_title(driver)
            sheet.update_cell(row, 3, position)

        row += 1


def findProfiles(driver, company):
    current_url = driver.current_url
    for profile in POSITIONS:
        try:
            new_url = "{}&title={}".format(current_url, profile)
            driver.get(new_url)
            randomWait(4, 8)
            results = int(driver.find_element_by_css_selector(CSS_SELECTOR['result']).text.split(" ")[0])

            for item in range(1, results + 1):
                driver.find_element_by_xpath(XPATHS['results'].format(item)).click()
                randomWait(4, 8)
                profile_url = driver.current_url
                try:
                    location = driver.find_element_by_css_selector(
                        "span.text-body-small.inline.t-black--light.break-words").text
                except Exception as ex:
                    # print(ex)
                    location = "Not Found"
                profile_heading = driver.find_element_by_css_selector(CSS_SELECTOR['profile_heading']).text
                position = job_title(driver)
                queryset = UsersData.objects.filter(linkedin_url=profile_url)

                if not len(queryset):
                    instance = UsersData(company=company, name=profile_heading, title=position, location=location,
                                         linkedin_url=profile_url, keyword=profile)

                    instance.save()
                    print(profile_heading, profile_url, "Saved Data")

                else:
                    print("User Data is already present", profile_heading)
                driver.get(new_url)
                randomWait(4, 8)
        except Exception as ex:
            # print(ex)
            pass

    return 0


def extractDomain(website):
    start = '//'
    end = '/'
    s = website
    website = s[s.find(start) + len(start):s.rfind(end)]

    if "www." not in website:
        domain = website
    else:
        domain = website.split("www.")[1]

    return domain


def companyInfo(driver, tab_name):

    try:
        linkedin_url = driver.current_url
        company_details = driver.find_element_by_css_selector(CSS_SELECTOR['company_detail'])
        company_details = company_details.text.splitlines()
        company_name = company_details[0]
        tagline = company_details[1]

        other_info = []
        try:
            for item in driver.find_elements_by_class_name(CLASS_NAMES['company_other_info']):
                other_info.append(item.text)

            industry = other_info[0]
            location = other_info[1]
            followers = other_info[2]
        except Exception as exp:
            industry = "NA"
            location = "NA"
            followers = "NA"

        emp = driver.find_element_by_css_selector(CSS_SELECTOR['employees'])
        employees = emp.text.split(" ")[2]

        try:
            website = driver.find_element_by_css_selector(CSS_SELECTOR['company_website']).get_attribute('href')

        except Exception as exp:
            website = "NA"

        instance = Companies(name=company_name, tagline=tagline, industry=industry,
                             location=location, followers=followers, employees=employees,
                             linkedin_url=linkedin_url, domain=website, keyword=tab_name)

        instance.save()
        print(company_name, instance, location, followers, website, employees)

    except Exception as ex:
        # print(ex)
        pass


def scrapEmpsData(driver):
    all_companies = Companies.objects.filter(data_scrapped="No")[2:100]
    print(len(all_companies))

    for company in all_companies:
        driver.get(company.linkedin_url)
        randomWait(2, 6)

        if clickOnAllEmployees(driver):
            findProfiles(driver, company)
        else:
            pass
        company.data_scrapped = "Yes"
        company.save()


def linkedinProfiles(driver, sheet_name, tab_name, column_number):
    companies, sheet = sheet_data(sheet_name, tab_name)

    row = 2
    for company in companies:
        try:
            linkedin_url = company['Company Linkedin']
            data_scrapped = company['Linkedin Data Scrapped']
            # company_name = company['SAAS Company Name']

            if len(linkedin_url) and linkedin_url != "NA" and not len(data_scrapped):
                queryset = Companies.objects.filter(linkedin_url=linkedin_url)

                if not len(queryset):
                    driver.get(linkedin_url)
                    companyInfo(driver, tab_name)
                    sheet.update_cell(row, column_number, "Yes")
                    wait(1)
                else:
                    print(linkedin_url, " - Data is already scrapped")
                    sheet.update_cell(row, column_number, "Yes")

        except Exception as ex:
            print(ex)

        row += 1


def verifyEmail(guess_email):
    return verify_email(guess_email)


def verifiedMails(all_guessed_emails):
    valid_emails = []

    for mail_id in all_guessed_emails:
        if verifyEmail(mail_id):
            valid_emails.append(mail_id)

    return valid_emails


def findValidEmails(first_name, last_name, domain):
    guess_email1 = "{}@{}".format(first_name, domain)
    guess_email2 = "{}.{}@{}".format(first_name, last_name, domain)
    guess_email3 = "{}_{}@{}".format(first_name, last_name, domain)
    guess_email4 = "{}{}@{}".format(first_name, last_name, domain)
    # guess_email5 = "{}{}@{}".format(first_name[0], last_name, domain)
    # guess_email6 = "{}{}@{}".format(first_name, last_name[0], domain)
    # guess_email7 = "{}.{}@{}".format(first_name, last_name[0], domain)
    # guess_email8 = "{}.{}@{}".format(first_name[0], last_name[0], domain)
    # guess_email9 = "{}{}@{}".format(first_name[0], last_name[0], domain)
    # guess_email10 = "{}@{}".format(last_name, domain)

    all_guessed_emails = [guess_email1, guess_email2, guess_email3, guess_email4]

    valid_emails = verifiedMails(all_guessed_emails)

    return valid_emails


def extractValidEmails():
    users = UsersData.objects.filter(valid_emails="NA")
    print(len(users))

    for user in users:
        try:
            domain = extractDomain(user.company.domain)
            name = user.name
            first_name = name.split(" ")[0]
            last_name = name.split(" ")[1]
            if "/" in domain:
                domain = domain.split("/")[0]

            print(name, domain)
            verified_emails = findValidEmails(first_name, last_name, domain)

            emails = ""
            if len(verified_emails) == 1:
                emails = verified_emails[0]
            elif not len(verified_emails):
                emails = "Not Found"
            else:
                for mail_id in verified_emails:
                    emails += "{}\n".format(mail_id)

            user.valid_emails = emails
            user.save()
            print("Saved")

        except Exception as ex:
            print(ex)


def exportData(sheet_name, tab_name):
    companies_list = []
    keywords = ["Service Companies", "Service Web", "Service Web US"]
    # keywords = ["React-India", "Python-India"]

    for item in keywords:
        companies = Companies.objects.filter(keyword=item)

        for company in companies:
            company_name = company.name
            companies_list.append(company_name)

    print(len(companies_list))

    all_data, sheet = sheet_data(sheet_name, tab_name)
    n = len(all_data)
    queryset = UsersData.objects.exclude(exported="Yes")

    rows = []
    for item in queryset:
        company_name = str(item.company)

        if company_name in companies_list:
            employees = str(item.company.employees)
            industry = str(item.company.industry)
            domain = str(item.company.domain)
            first_name = str(item.name).split(" ")[0]
            last_name = str(item.name).split(" ")[1]
            row_data = [first_name, last_name, str(item.keyword), str(item.title), company_name, str(item.linkedin_url), str(item.location),
                        employees, industry, domain]

            print(row_data)
            rows.append(row_data)
            item.exported = "Yes"
            item.save()

    sheet.insert_rows(rows, 2 + n)


def add_note(driver, request_sent, message):
    try:
        # add note
        driver.find_element_by_css_selector(CSS_SELECTOR['add_note_button']).click()

        note_area = driver.find_element_by_css_selector(CSS_SELECTOR['note_area'])
        random_wait(2, 5)
        # print(message)
        note_area.send_keys(message)
        random_wait(2, 5)

        # send button
        driver.find_element_by_css_selector(CSS_SELECTOR['send_button']).click()
        request_sent = True
        random_wait(2, 5)
        return request_sent
    except:
        return request_sent


def inside_connect_button(driver, request_sent, message):
    try:
        driver.find_element_by_css_selector(CSS_SELECTOR['connect_inside_button']).click()
        random_wait(2, 5)
        request_sent = add_note(driver, request_sent, message)
        return request_sent

    except:
        return request_sent


def more_button(driver, request_sent, message):
    try:
        # Click on more button
        j = 0
        for item in driver.find_elements_by_css_selector(CSS_SELECTOR['more_button']):
            if j == 1:
                item.click()
            j += 1
        random_wait(2, 5)

        i = 1
        for item in driver.find_elements_by_css_selector(CSS_SELECTOR['more_button_dropdown']):
            # print(item.text)
            if item.text == "Connect":
                item.click()
                random_wait(2, 5)
            i += 1

        request_sent = inside_connect_button(driver, request_sent, message)
        return request_sent

    except:
        return request_sent


def check_user(driver, message):
    request_sent = False
    try:
        random_wait(2, 5)
        buttons = driver.find_element_by_class_name('pvs-profile-actions ').text.splitlines()
        if buttons[0].lower() == "message":
            request_sent = more_button(driver, request_sent, message)

        else:
            driver.find_element_by_css_selector(CSS_SELECTOR['connect_button']).click()
            random_wait(2, 5)
            request_sent = add_note(driver, request_sent, message)

        return request_sent
    except:
        return request_sent


def send_connection_request(driver, sheet_name, tab_name, connect_limit):
    all_data, sheet = sheet_data(sheet_name, tab_name)

    row = 2
    count = 0
    for data in all_data:
        li_url = data['LinkedinUrl']
        already_sent = data['Linkedin Request Sent']

        try:
            if len(li_url) and not len(already_sent) and count < connect_limit:
                print(row, li_url)
                driver.get(li_url)
                first_name = driver.find_element_by_css_selector(CSS_SELECTOR['profile_heading']).text.split(" ")[0]
                if check_user(driver, message.format(first_name)):
                    print("Follow count - ", count)
                    sheet.update_cell(row, 9, "Yes")
                    count += 1
                else:
                    sheet.update_cell(row, 9, "Not able to sent")

        except:
            sheet.update_cell(row, 9, "Not able to sent")

        row += 1


def export_companies(sheet_name, tab_name):
    qs = Companies.objects.all()

    rows_data = []

    for item in qs:
        rows_data.append([item.name])

    all_data, sheet = sheet_data(sheet_name, tab_name)
    n = len(all_data)

    sheet.insert_rows(rows_data, n+2)


# export_companies(SAAS_SHEET, "Companies")

def remove_data():
    all_data, sheet = sheet_data(SAAS_SHEET, "Prospects")

    linkedin_urls = []

    for data in all_data:
        url = data['Linkedin Profile']
        linkedin_urls.append(url)

    print(len(linkedin_urls))
    linkedin_urls = set(linkedin_urls)
    print(len(linkedin_urls))

    # for url in linkedin_urls:
    #     print(url)

    all_data, sheet = sheet_data(SAAS_SHEET, "All Data")

    row = 2
    for data in all_data:
        url = data['Linkedin Url']
        if url in linkedin_urls:
            sheet.delete_row(row)
            print("Removed", url)
            wait(0.5)
        else:
            row += 1


def demo():
    cm = Companies.objects.all()
    qs = UsersData.objects.all()

    print(len(qs))
    print(len(cm))


# remove_data()
