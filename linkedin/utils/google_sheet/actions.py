import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .constants import CREDS_FILE_LOCATION, SCOPE


def sheet_data(sheet_name, tab_name):
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE_LOCATION, SCOPE)

    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).worksheet(tab_name)
    data = sheet.get_all_records()

    return data, sheet

