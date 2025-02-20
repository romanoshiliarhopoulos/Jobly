import requests
from bs4 import BeautifulSoup
import random
import time
import pandas as pd
import json


print("Running.....")
# Job search parameters
#titles = ["Software Engineering Intern", "Software Developer Intern", "Backend Developer Intern", "Full Stack Intern"]
#locations = ["New York, NY", "San Francisco, CA", "Seattle, WA", "Boston, MA", "Austin, TX"]

titles = ["Software Engineering Intern", "Software Development Intern"]
locations = ["United States"]
total_jobs = 600  # Maximum number of jobs to fetch
increment = 25  # LinkedIn paginates in multiples of 25

# User-Agent rotation
headers_list = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/87.0"},
]
# List to store job IDs
id_list = []

# Fetch job postings
print("Looking for jobs! ....")
for title in titles:
    for location in locations:
        for start in range(0, total_jobs, increment):
            print(".")
            list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
            headers = random.choice(headers_list)
            response = requests.get(list_url, headers=headers)

            if response.status_code != 200:
                print(f"Error fetching page {start} for {location}: {response.status_code}")
                continue  # Skip to next page if there's an error

            list_soup = BeautifulSoup(response.text, "html.parser")
            page_jobs = list_soup.find_all("li")

            for job in page_jobs:
                base_card_div = job.find("div", {"class": "base-card"})
                if base_card_div:
                    job_id = base_card_div.get("data-entity-urn").split(":")[3]
                    if job_id not in id_list:
                        id_list.append(job_id)

            # Sleep to avoid being blocked
            print(".")
            time.sleep(random.uniform(2, 4))

print(f"Total unique job IDs collected: {len(id_list)}")
print("All the ids are: ")
print(id_list)

# Initialize job information list
job_list = []
companies_seen = set()

# Fetch job details
for job_id in id_list:
    print("getting info for job: ", job_id)
    print("...")
    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    headers = random.choice(headers_list)
    job_response = requests.get(job_url, headers=headers)

    if job_response.status_code != 200:
        print(f"Error fetching job {job_id}: {job_response.status_code}")
        continue

    job_soup = BeautifulSoup(job_response.text, "html.parser")
    job_post = {}

    # Extract job details
    try:
        job_post["job_title"] = job_soup.find("h2", {"class": "top-card-layout__title"}).text.strip()
    except:
        job_post["job_title"] = None

    try:
        job_post["company_name"] = job_soup.find("a", {"class": "topcard__org-name-link"}).text.strip()
    except:
        job_post["company_name"] = None

    try:
        job_post["time_posted"] = job_soup.find("span", {"class": "posted-time-ago__text"}).text.strip()
    except:
        job_post["time_posted"] = None

    try:
        job_post["num_applicants"] = job_soup.find("span", {"class": "num-applicants__caption"}).text.strip()
    except:
        job_post["num_applicants"] = None
        # Extract job description
    try:
        description_div = job_soup.find("div", {"class": "description__text description__text--rich"})
        job_post["description"] = description_div.text.strip() if description_div else None
    except:
        job_post["description"] = None
    job_post["Job-Id"] = job_id
    
    '''
    # Avoid duplicate company listings
    if job_post["company_name"] and job_post["company_name"] not in companies_seen:
        companies_seen.add(job_post["company_name"])
        '''
    job_list.append(job_post)
        
    
    # Sleep between requests
    time.sleep(random.uniform(2, 4))

# Print results
print(f"Total jobs scraped: {len(job_list)}")
print(job_list)

 # Save to JSON file
with open("jobs2.json", "w") as f:
    json.dump(job_list, f, indent=2)

print("Job data saved to jobs.json")

