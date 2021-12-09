import json
import requests
from .models import Companies, UsersData


ZERO_BOUNCE_API_KEY = "a76ce2b0f1344f3f9d252e1a091162f3"
ZERO_BOUNCE_URL = "https://api.zerobounce.net/v2/validate"
ip_address = ""  # ip_address can be blank
catch_all_domains = []


def find_users_valid_email(keywords):
    companies_qs = Companies.objects.filter(keyword__in=keywords)
    print(len(companies_qs))
    users_queryset = UsersData.objects.filter(company__in=companies_qs, valid_emails="NA",
                                              company__keyword__in=keywords)
    print(len(users_queryset))

    i = 1
    for user_obj in users_queryset:
        name = user_obj.name.split(" ")
        if len(name) >= 2:
            first_name = name[0]
            last_name = name[1]

            website_url = user_obj.company__domain
            is_valid, domain = find_domain(website_url)
            print(i, is_valid, domain)

            if is_valid:
                email_pnc_list = email_pnc(first_name, last_name, domain)
                valid_email = find_valid_email(email_pnc_list, domain)
                user_obj.valid_emails = valid_email
                user_obj.save()

            else:
                user_obj.valid_emails = "Invalid Domain"
                user_obj.save()

        else:
            user_obj.valid_emails = "Naming Error"
            user_obj.save()

        i += 1


def find_domain(website_link):
    is_valid = False
    domain = "NA"

    try:
        if "www" in website_link:
            domain = website_link.split("//")[1].replace("/", "").split("www.")[1]

            if "?utm_source" in domain:
                domain = domain.split("?utm_source")[0]

            for counter in range(len(domain)):
                if domain[counter:counter + 4] == ".com":
                    domain = domain[:counter + 4]

                elif domain[counter:counter + 3] == ".in" or domain[counter:counter + 3] == ".io":
                    domain = domain[:counter + 3]

        else:
            domain = website_link.split("//")[1].replace("/", "")

            if "?utm_source" in domain:
                domain = domain.split("?utm_source")[0]

            for counter in range(len(domain)):
                if domain[counter:counter + 4] == ".com":
                    domain = domain[:counter + 4]

                elif domain[counter:counter + 3] == ".in" or domain[counter:counter + 3] == ".io":
                    domain = domain[:counter + 3]

        is_valid = True
    except Exception as ex:
        print(ex)

    if "linkedin" in domain or "bit.ly" in domain or "." not in domain or ".ly" in domain:
        is_valid = False

    return is_valid, domain


def email_pnc(first_name, last_name, domain):
    guess_email1 = "{}@{}".format(first_name, domain)
    guess_email2 = "{}.{}@{}".format(first_name, last_name, domain)
    guess_email3 = "{}{}@{}".format(first_name, last_name, domain)
    guess_email4 = "{}{}@{}".format(first_name[0], last_name, domain)
    guess_email5 = "{}{}@{}".format(first_name, last_name[0], domain)

    email_pnc_list = [guess_email1, guess_email2, guess_email3, guess_email4, guess_email5]

    return email_pnc_list


def find_valid_email(email_pnc_list, domain):
    valid_email = "Not Found"

    for email in email_pnc_list:
        params = {"email": email, "api_key": ZERO_BOUNCE_API_KEY, "ip_address": ip_address}
        response = requests.get(ZERO_BOUNCE_URL, params=params)
        status = json.loads(response.content)['status']
        print(email, status)

        if status == "valid":
            valid_email = email
            break

        if status == "catch-all":
            valid_email = "Catch-All"
            catch_all_domains.append(domain)
            break

    return valid_email
