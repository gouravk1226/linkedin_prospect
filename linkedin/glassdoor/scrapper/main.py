from utils.common_actions.actions import chrome_driver
from .constants import URLS
from .actions import jobs


my_driver = chrome_driver()
jobs(my_driver, URLS['android_dev_india'], "Android India")
