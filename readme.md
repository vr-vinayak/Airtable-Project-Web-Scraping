# Overview:

> The project aim to scarping various job details from linkhub.com and insert the extracted data to airtable, updating and deleting record , primarily implementing pyairtable, python,selenium, Beautifulsoup,requests modules.


# Local setup of all requirements for running the airtable script.
Create virtual enviorment 

### For Linux in terminal
    sudo apt install python3.8-venv
    source sftp_venv/bin/activate

### For Windows in cmd(command prompt)
    python -m venv airtable_env
    cd airtable_env/Scripts
    activate


#  Also you need to download the geckodriver for webdriver.firefox(executable_path="geckodriver exe file path") to use selenium.

1. You can download the geckodriver from this specified link given https://github.com/mozilla/geckodriver/releases
   as per your operating system(download .zip file for windows and tar. file for linux).

   for chrome:

   https://chromedriver.chromium.org/downloads


2. After downloading try to unzip the zip file, make a new folder naming "geckodriver" and paste the geckodriver.exe 
   file under it.

3. Finally just specify the full path in this given statment in your script "driver = webdriver.Firefox(executable_
   path="Your full path\\geckodriver.exe",options=fireFoxOptions)" to where ever your geckodriver folder is and 

   for chrome:

    path="Your full path\\chromedriver.exe")"



# After creating venv and activating your venv, go to the directory where ever you project is saved, than  execute below command in your local machine.

### For Windows:
    pip install -r requirements.txt
    python salesforcejobs.py

### For Linux:
    pip3 install -r requirements.txt
    python3 salesforcejobs.py


# For any changes you can configurate in config.py file.

### Below are the variables in which you can config.
> AIRTABLE_API_URL = "https://api.airtable.com/v0/appgtgvgqCBONn9yc/Job Postings Staging"
> AIRTABLE_KEY = "keytkiupqAh5ct7tZ"  #Your api key
> BASE_ID = "appgtgvgqCBONn9yc"       #Your base id
> TABLE_NAME = "Job Postings Staging" #Your Tablename
> JOB_START_DATE = "Your config" #datetime.now()
> JOB_NO_TO_CRAWL = "Your config" #1
> page = "Your config" #1 
> MAX_RETRY = "Your config" #3
> TOTAL_PAGE_EXPLORE = "Your config" #100
> AIRTABLE_INSERT_ROW_LENGTH = "Your config" #100




