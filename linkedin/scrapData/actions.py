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
    # driver_location = "/usr/bin/chromedriver"
    driver_location = "/home/gourav/Downloads/drivers/chromedriver"
    binary_location = "/usr/bin/google-chrome"

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
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
            # print(ex)
            pass
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


def job_title_non_premium(driver, company_name):
    experience = driver.find_elements_by_css_selector(
        'section.pv-profile-section.pv-profile-section--reorder-enabled.background-section.artdeco-card.mt4.ember-view')[
        0].text.splitlines()

    position = experience[2]
    if position.lower() == company_name.lower():
        position = experience[6]

    else:
        position = experience[1]

    return position


def job_title_premium(driver, company_name):
    experience = driver.find_elements_by_css_selector('section.artdeco-card.ember-view.break-words.mt4.pb3')[
        2].text.splitlines()

    position = experience[2]
    if position.lower() == company_name.lower():
        position = experience[6]

    return position


def job_title(driver, company_name, profile, is_premium):
    position = "Not Found"
    try:
        for i in range(10):
            driver.execute_script(f"window.scrollTo(0, {i * 100})")
            wait(0.1)

        wait(2)
        if is_premium:
            position = job_title_premium(driver, company_name)

        else:
            position = job_title_non_premium(driver, company_name)

        if profile.lower() not in position.lower():
            print(profile, position)
            position = "Mis-Matched"

    except Exception as ex:
        print(ex)

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
    company_name = company.name
    for profile in POSITIONS:
        print(company_name, profile)
        try:
            new_url = "{}&geoUrn=%5B\"102713980\"%5D&title={}".format(current_url, profile)
            driver.get(new_url)
            randomWait(15, 20)
            results = int(driver.find_element_by_css_selector(CSS_SELECTOR['result']).text.split(" ")[0])

            for item in range(1, results + 1):
                if results==1:
                    try:
                        target = driver.find_element_by_xpath(XPATHS['result'].format(1)).get_attribute('href')
                    except:
                        pass
                try:
                    target = driver.find_element_by_xpath(XPATHS['results'].format(1, item)).get_attribute('href')
                except:
                    target = driver.find_element_by_xpath(XPATHS['results'].format(3, item)).get_attribute('href')
                if "headless" not in target:
                    target = target.split("?miniProfile")[0]
                    print(target)
                    queryset = UsersData.objects.filter(linkedin_url=target)

                    if not len(queryset):
                        driver.get(target)
                        randomWait(8, 12)
                        profile_url = driver.current_url
                        try:
                            location = driver.find_element_by_css_selector(
                                "span.text-body-small.inline.t-black--light.break-words").text
                        except Exception as ex:
                            print(ex)
                            location = "Not Found"
                        profile_heading = driver.find_element_by_css_selector(CSS_SELECTOR['profile_heading']).text
                        position = job_title(driver, company_name, profile, False)

                        queryset = UsersData.objects.filter(linkedin_url=profile_url)

                        if not len(queryset):
                            instance = UsersData(company=company, name=profile_heading, title=position,
                                                 location=location,
                                                 linkedin_url=profile_url, keyword=profile)

                            instance.save()
                            print(profile_heading, profile_url, "Saved Data")

                        else:
                            print("User Data is already present", profile_heading)


                    else:
                        print("Already Present")

                driver.get(new_url)
                randomWait(8, 12)
        except Exception as ex:
            print(ex)
            # print(ex)
            pass

    return 0


def findProfilesPremium(driver, company):
    current_url = driver.current_url
    for profile in POSITIONS:
        new_url = f"{current_url}&geoUrn=%5B%22101174742%22%2C%22105149290%22%2C%2290009551%22%2C%22100025096%22%2C%22104444106%22%5D&title={profile}"
        driver.get(new_url)
        randomWait(15, 30)
        try:
            results = int(driver.find_element_by_css_selector(CSS_SELECTOR['result']).text.split(" ")[0]) + 1
        except Exception as ex:
            results = None

        if results:
            for i in range(1, results):
                try:
                    if i == 1:
                        target = driver.find_element_by_xpath(XPATHS['results_1']).get_attribute('href')

                    else:
                        target = driver.find_element_by_xpath(XPATHS['results_2'].format(i)).get_attribute('href')

                    target = target.split("?miniProfile")[0]
                    queryset = UsersData.objects.filter(linkedin_url=target)

                    if not len(queryset):
                        driver.get(target)
                        randomWait(8, 12)
                        profile_url = driver.current_url

                        try:
                            location = driver.find_element_by_css_selector(
                                "span.text-body-small.inline.t-black--light.break-words").text
                        except:
                            location = "Not Found"

                        profile_heading = driver.find_element_by_css_selector(CSS_SELECTOR['profile_heading']).text
                        position = job_title(driver)
                        queryset = UsersData.objects.filter(linkedin_url=profile_url)

                        if not len(queryset):
                            instance = UsersData(company=company, name=profile_heading, title=position,
                                                 location=location,
                                                 linkedin_url=profile_url, keyword=profile)

                            instance.save()
                            print(profile_heading, profile_url, "Saved Data")

                        else:
                            print("User Data is already present", profile_heading)

                    driver.get(new_url)
                    randomWait(8, 12)

                except Exception as ex:
                    # print(ex)
                    pass


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
    is_scrapped = False
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
        is_scrapped = True
        print(company_name, instance, location, followers, website, employees)

    except Exception as ex:
        print("Exception - ", ex)

    return is_scrapped


def companies_info(driver, sheet_name, tab_name):
    companies, sheet = sheet_data(sheet_name, tab_name)

    row = 2
    for company in companies:
        try:
            linkedin_url = company['Agency LinkedIn']
            li_emp = company['NO. OF EMPLOYEES ON LINKEDIN']
            city = company['City']

            if len(linkedin_url) and (li_emp != "" or not len(city)) and row > 54:
                driver.get(linkedin_url)
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
                print(row, linkedin_url, employees, location)
                if li_emp == "":
                    sheet.update_cell(row, 8, employees)
                if not len(city):
                    sheet.update_cell(row, 5, location)
                wait(5)
        except Exception as ex:
            print(ex)

        row += 1


def scrapEmpsData(driver, is_premium):
    # findProfiles(driver, 'company')
    # keywords = ["adzuna"]
    keywords = ["Linkedin-jobs-Reactjs", "Django", "JavaScript", "Indian_Startup_Result",'entracker','shine_Java']
    for keyword in keywords:
        all_companies = Companies.objects.filter(data_scrapped="No", keyword=keyword)
        print(len(all_companies))

        for company in all_companies[::-1]:
            driver.get(company.linkedin_url)
            randomWait(4, 10)

            if clickOnAllEmployees(driver):
                if is_premium:
                    findProfilesPremium(driver, company)
                else:
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
            linkedin_url = company['Company LinkedIn']
            data_scrapped = company['Data Scrapped']

            if row > 0 and len(linkedin_url) and linkedin_url != "NA" and linkedin_url != "Error" and not len(
                    data_scrapped):
                print(row)
                queryset = Companies.objects.filter(linkedin_url=linkedin_url)

                if not len(queryset):
                    driver.get(linkedin_url)
                    if companyInfo(driver, tab_name):
                        sheet.update_cell(row, column_number, "Yes")
                    else:
                        sheet.update_cell(row, column_number, "Already Scrapped")
                    wait(1)
                else:
                    print(linkedin_url, " - Data is already scrapped")
                    sheet.update_cell(row, column_number, "Already Scrapped")

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
    keywords = ["Django", "Django-India-All", "Java-India-All",
                "React Js-India-All", "Android-India-All", "Python-India-All",
                "React Js-India-WeWorkRemotely", "React Js-India-RemoteOk", "JavaScript", "Indian_Startup_Result",
                "Linkedin-jobs-Reactjs","entracker","java_script","android","django","react","node","adzuna","shine_Java"]
    companies = Companies.objects.filter(keyword__in=keywords)
    print(len(companies))
    all_data, sheet = sheet_data(sheet_name, tab_name)
    n = len(all_data)
    queryset = UsersData.objects.filter(exported="NA", company__keyword__in=keywords)
    print(len(queryset))

    rows = []
    for item in queryset:
        company_name = str(item.company)
        keyword = str(item.company.keyword)
        employees = str(item.company.employees)
        industry = str(item.company.industry)
        domain = str(item.company.domain)
        email = item.valid_emails
        first_name = str(item.name).split(" ")[0]
        try:
            last_name = str(item.name).split(" ")[1]
        except Exception as ex:
            print(ex)
            last_name = ""
        row_data = [first_name, last_name, str(item.keyword), str(item.title), company_name, str(item.linkedin_url),
                    str(item.location),
                    employees, industry, domain, keyword]

        print(row_data)
        rows.append(row_data)
        item.exported = "Yes"
        item.save()

    print(len(rows))
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

    sheet.insert_rows(rows_data, n + 2)


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
