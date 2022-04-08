import os
import sys
import json
import time
import urllib3

# custom modules
import utils
import configs  ### This module will have all the configurations

import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pyairtable import Api, Base, Table 

urllib3.disable_warnings()


"""
    To connect to airtable using table module from pyairtable class, passing all parameters from config module
"""
payload_airtable = Table(configs.AIRTABLE_KEY, configs.BASE_ID, configs.TABLE_NAME)


class SalesForceJobs:
    def __init__(self):
        self.airtable_jobs_cache = None
        self.job_ids_need_to_update = []
        self.jobs_need_to_create = []
        self.all_linkup_job_ids = []
    
    """
        Fetch all records from airtable
    """

    def fetch_airtable_jobs(self):
        data = payload_airtable.all()
        # # print(data)
        self.airtable_jobs_cache = {r["fields"]["uuid"]:
                    {"id": r["id"], "posted_date":r["fields"]["posted_date"], "last_synced_at":r["fields"]["last_synced_at"], "createdTime":r["createdTime"] } 
                    for r in data if r.get("fields").get("uuid")}
                    
        print(f'==================== Airtable records fetched from {configs.TABLE_NAME} ==================== \n')
        # print(self.airtable_jobs_cache)
 

    """
        Pulling latest jobs
    """
    def pull_latest_jobs(self):  
        while (True and configs.PAGE <= configs.TOTAL_PAGE_EXPLORE):
            page_url = f"https://www.linkup.com/search/results/salesforce-jobs?title_contains=salesforce&pageNum={configs.PAGE}"
            retry_count = 0
            print(f"\nStart processing for page - {page_url}")
            time.sleep(1)
            soup = utils.get_page_source_using_selenium(page_url)
            all_jobs_on_page = soup.find_all("div", class_="row job-listing")
            if not all_jobs_on_page:
                print(soup)
                print("No job found so stopping process....")
                break


            for job in all_jobs_on_page[:configs.JOB_NO_TO_CRAWL]:  ###[:5]
                # print("JOB: ",job)
                job_href = job.find('h4').find('a', class_='organic-link search-result-link')
                job_id = job_href['href'].split('/')[-1]
                if not job_id:
                    job_id = job_href['href'].split('details/')[1].replace("/", "")
                self.all_linkup_job_ids.append(job_id)

                data = job.find('p', class_='f-s-14')
                job_detail = data.find_all('span', class_='semi-bold')
                posted_date_str = job_detail[2].text.strip()
                posted_date = utils.get_posted_date(posted_date_str)
                
                if job_id in sfj.airtable_jobs_cache and sfj.airtable_jobs_cache[job_id]['posted_date'] < posted_date:
                    print("job id need to update: ", job_id, posted_date, sfj.airtable_jobs_cache[job_id]['posted_date'])
                    self.job_ids_need_to_update.append(job_id)
                elif job_id not in sfj.airtable_jobs_cache:  
                    print('job id need to create: ', job_id)
                    self.jobs_need_to_create.append(job_id)
                else:
                    print('pull_latest_jobs: all good')

            configs.PAGE += 1

        return 

    """
          Check updated record to push in airtable
    """
    
    def updated_jobs_to_airtable(self,job_ids_need_to_update):
        page_list = []
        job_ids = []
        for job_id in job_ids_need_to_update:
            print("\nJOb id ", job_id)
            job_link = "https://www.linkup.com/details/"+job_id                
            page_jobs_detail = self.get_job_detail(job_link)

            print("\n id is: ",self.airtable_jobs_cache[job_id]['id'])
            if page_jobs_detail and page_jobs_detail['uuid']:
    
                page_list.append({'id': self.airtable_jobs_cache[job_id]['id'], 'fields': page_jobs_detail})
                job_ids.append(job_id)


        print(" ***************** Job needs to be updated into airtable ****************")
        #print(page_list)
        self.push_updated_records_to_airtable(page_list)
        

    """
        Create new jobs to push in airtable
    """

    def create_new_jobs(self, jobs_need_to_create):
        page_list, job_ids = [], []
        for job_id in jobs_need_to_create:
            job_link = "https://www.linkup.com/details/"+job_id            
            page_jobs_detail = self.get_job_detail(job_link)
            if page_jobs_detail and page_jobs_detail['uuid']:
                page_list.append(page_jobs_detail)
                job_ids.append(job_id)

        print(" ***************** New Job need to create into airtable ****************")
        if page_list:
            payload_airtable.batch_create(page_list)
            print("\n Total record pushed in airatable :", len(page_list))

        
    """
        Push all updated records to airtable only if updated/modified
    """
       
    def push_updated_records_to_airtable(self, page_jobs_detail_list):
        print("Updating the existing records in airtable")
        if page_jobs_detail_list:
            payload_airtable.batch_update(page_jobs_detail_list)
            print("\n Total records updated in airatable :",len(page_jobs_detail_list))


    """
        Getting the job apply links
    """
    def get_job_url(self,apply_link):
        time.sleep(1)
        r = requests.get(apply_link, verify=False)
        #print("\nget_job_url:res.status_code:", r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        scripts = soup.find_all("script")
        for s in scripts:
            if 'location.href' in s.text:
                return s.text.split('location.href = "')[1].split('" ;')[0]



    """
        Get all jobs details using selenium
    """

    def get_job_detail(self, job_link):
        time.sleep(1)
        soup = utils.get_page_source_using_selenium(job_link)

        print("job_link:", job_link)
        uuid = job_link.split("/")[-1]
        job_title = soup.find("div", class_="job-header").find("h2", class_= "title").text.strip()
        company_name = soup.find("div", class_="job-header").find("h6", class_= "company").text.strip()
        job_location = soup.find("div", class_="job-header").find("h6", class_= "location").text.strip()
        apply_link = soup.find("a", class_= "apply-link").get('href')
        job_posted_date = soup.find("div", class_="job-header").find("h6", class_= "date-posted").text.strip()
        job_html_description = soup.find("div", class_= "job-description")        
        location = job_location.split(',')

        record = {
            "uuid": uuid, 
            "job_title": job_title, 
            "job_location": job_location,
            "apply_url": self.get_job_url(apply_link) , 
            "job_city": job_location.split(',')[0], 
            "job_state": location[1] if len(location)>1 else '', 
            "company_name": company_name, 
            "job_description": job_html_description.text.strip(), 
            "job_html_description": str(job_html_description), 
            "posted_date": utils.get_posted_date(job_posted_date),
            "crawl_time": configs.JOB_START_DATE.strftime("%Y-%m-%dT%H:%M:%S"),
            "last_synced_at": datetime.now().date().strftime("%Y-%m-%dT%H:%M:%S")
        }

        return record



    """
        Create new jobs
    """
    def push_new_jobs_to_airtable(self):
        if self.jobs_need_to_create :
            print(f"*********** \nTotal news jobs to be created: {len(self.jobs_need_to_create)}")
            chunks_jobs_need_to_create = utils.chunks(self.jobs_need_to_create, configs.AIRTABLE_INSERT_ROW_LENGTH)
            for sub_list in chunks_jobs_need_to_create:
                print(f"\t start(creating) pushing chunk of jobs: {len(sub_list)}")
                sfj.create_new_jobs(sub_list)
        else:
            print("*********** No New Job to create ************")


    """
        Update existing record
    """
    def update_airtable_jobs(self):
        if self.job_ids_need_to_update:
            print(f"************* Total jobs that will be updated :{len(self.job_ids_need_to_update)}")
            total_upate_jobs = len(self.job_ids_need_to_update)
            list_with_sub_update_list = utils.chunks(self.job_ids_need_to_update, configs.AIRTABLE_INSERT_ROW_LENGTH)

            for sub_update_list in list_with_sub_update_list:
                print(f"\t start(updating) pushing chunk of jobs: {len(sub_update_list)}")
                sfj.updated_jobs_to_airtable(sub_update_list)

        else:
            print("*************** No Jobs to be updated **************")


    """
        Delete jobs from airtable
    """

    def delete_jobs_from_airtable(self):
    
        print("airtable_jobs_cache: ", self.airtable_jobs_cache.keys())
        print("all_linkup_job_ids: ", self.all_linkup_job_ids)
        difference = set(self.airtable_jobs_cache.keys()).difference(set(self.all_linkup_job_ids))
        #print("differenceself ", difference)
        deleted_ids  = []
        for job_id in difference:
            deleted_ids.append(self.airtable_jobs_cache[job_id]['id'])
        print(f'id to be deleted: {deleted_ids}')
        if deleted_ids:
            payload_airtable.batch_delete(deleted_ids)
        else:
            print("Nothing to delete")



# ---- Job starts from here-----

if __name__ == "__main__":
    sfj = SalesForceJobs()

    # If aleady jobs available to create then lets create first
    with utils.Timer('REFRESH TABLE'):
        sfj.fetch_airtable_jobs()

    """ Fetch all linkhub jobs """

    with utils.Timer('Fetching linkhub jobs'):
        sfj.pull_latest_jobs()

    """  Create new job """

    with utils.Timer('CREATE NEW JOB INTO AIRTABLE'):
        sfj.push_new_jobs_to_airtable()

    """ To Update records """

    with utils.Timer("Updating existing records"):
        sfj.update_airtable_jobs()

    """    To delete jobs    """

    # with utils.Timer("Deleting jobs from airtable"):
    #     sfj.delete_jobs_from_airtable()


    # print(sfj.job_ids_need_to_update)
    #print(sfj.jobs_need_to_create)

    print('Done')

