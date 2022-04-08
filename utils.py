import time

from timeit import default_timer
from dateutil.relativedelta import relativedelta
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options ### To add headless option
from bs4 import BeautifulSoup
import configs

    
class Timer(object):
    def __init__(self, name=None, verbose=False):
        self.verbose = verbose
        self.timer = default_timer
        self.name = name
        
    def __enter__(self):
        print(f'**************  Starting process {self.name} *************')
        self.start = self.timer()
        return self
        
    def __exit__(self, *args):
        end = self.timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000  # millisecs
        print(f'**************  Completed {self.name} with elapsed time: {self.elapsed} ms  ************')



def get_posted_date(str_days_ago):
    import datetime
    str_days_ago = str_days_ago.replace("+", "").replace("Posted", "")
    TODAY = datetime.date.today()
    splitted = str_days_ago.split()
    if len(splitted) == 1 and splitted[0].lower() == 'today':
        return (TODAY).strftime("%Y-%m-%dT%H:%M:%S")
    elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
        date = TODAY - relativedelta(days=1)
        return (date).strftime("%Y-%m-%dT%H:%M:%S")
    elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
        date = datetime.datetime.now() - relativedelta(hours=int(splitted[0]))
        return (date.date()).strftime("%Y-%m-%dT%H:%M:%S")
    elif splitted[1].lower() in ['day', 'days', 'd']:
        date = TODAY - relativedelta(days=int(splitted[0]))
        return (date).strftime("%Y-%m-%dT%H:%M:%S")
    elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
        date = TODAY - relativedelta(weeks=int(splitted[0]))
        return (date).strftime("%Y-%m-%dT%H:%M:%S")
    elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
        date = TODAY - relativedelta(months=int(splitted[0]))
        return (date).strftime("%Y-%m-%dT%H:%M:%S")
    elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
        date = TODAY - relativedelta(years=int(splitted[0]))
        return (date).strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return ""

def chunks(lst, chunk_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_page_source_using_selenium(link):
    soup = None
    retry_count = 0
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.headless = True
    WAIT_TIME_OUT = 1
    while retry_count < configs.MAX_RETRY:

        """
            below firefoxoptions.headless will restrict opening  firefoxbrowser everytime
        """
        driver = webdriver.Firefox(executable_path= configs.executable_path,options=fireFoxOptions)
        #driver = webdriver.Firefox(executable_path="./geckodriver")

        driver.implicitly_wait(0.5)
        driver.get(link)
        time.sleep(1)
        driver.refresh()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # print(soup.text)
        driver.close()
        if 'Request unsuccessful. Incapsula incident ID' not in soup.text:
            print(' ******************** Page Has Content so stoping loop and process it *****************')
            break
        else:
            retry_count  = retry_count + 1
            print(f"###### Retrying {retry_count}")
            time.sleep(WAIT_TIME_OUT+retry_count)
        # driver.close()
        
    if retry_count == configs.MAX_RETRY:
        print('Unable to get data from page so saving page number and other objects')

    return soup
