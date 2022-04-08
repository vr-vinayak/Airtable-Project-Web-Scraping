from datetime import datetime

"""Here you can do all the configurations"""

AIRTABLE_API_URL = "https://api.airtable.com/v0/appgtgvgqCBONn9yc/Job Postings Staging"
AIRTABLE_KEY = "keytkiupqAh5ct7tZ"  

BASE_ID = "appgtgvgqCBONn9yc"

TABLE_NAME = "Job Postings Staging"

JOB_START_DATE = datetime.now()

PAGE = 1
MAX_RETRY = 4
JOB_NO_TO_CRAWL = 26
TOTAL_PAGE_EXPLORE = 100
AIRTABLE_INSERT_ROW_LENGTH = 20

""" For webdriver executable path for firefox geckodriver.exe file  """
executable_path="D:\\Projects\\geckodriver\\geckodriver.exe"
print(executable_path)