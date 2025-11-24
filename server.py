from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import time
import uvicorn
from collections import Counter
import re

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def robust_get(url,params,headers):
    for i in range(3):
        try:
            return requests.get(url,params=params,headers=headers,timeout=5)
        except requests.exceptions.RequestException:
            time.sleep(2)
    return None

def extract_salary(description_text):
    salary_pattern=r'\$[\d,]+(?:k|K)?(?:\s*-\s*\$[\d,]+(?:k|K)?)?'
    matches=re.findall(salary_pattern,description_text)
    if matches:
        return max(matches,key=len)
    return "Not Listed"

def scrape_linkedin_jobs(query:str,location:str):
    base_url="https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    skills_to_track=['python','sql','aws','react','docker','java']
    found_skills=[]
    all_jobs=[]  
    for start in [0,25]:
        params={
            "keywords":query,
            "location":location,
            "f_TPR":"r86400",
            "start":start
        }
        response=robust_get(base_url,params,headers)
        if not response:
            continue
        try:
            response.raise_for_status()
            soup=BeautifulSoup(response.text,"html.parser")
            job_cards=soup.find_all("li")
            for card in job_cards:
                try:
                    title_tag=card.find("h3",class_="base-search-card__title")
                    title=title_tag.text.strip() if title_tag else "N/A"
                    for kw in skills_to_track:
                        if kw in title.lower():
                            found_skills.append(kw)
                    company_tag=card.find("h4",class_="base-search-card__subtitle")
                    company=company_tag.text.strip() if company_tag else "N/A"
                    location_tag=card.find("span",class_="job-search-card__location")
                    job_location=location_tag.text.strip() if location_tag else "N/A"
                    time_tag=card.find("time")
                    posted_date=time_tag.text.strip() if time_tag else "N/A"
                    link_tag=card.find("a",class_="base-card__full-link")
                    link=link_tag["href"] if link_tag else "#"
                    description_snippet=card.get_text()
                    salary=extract_salary(description_snippet)

                    all_jobs.append({
                        "title":title,
                        "company":company,
                        "location":job_location,
                        "posted_date":posted_date,
                        "link":link,
                        "salary":salary
                    })

                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue

            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Network error:{e}")
            continue

    return all_jobs,dict(Counter(found_skills))

def scrape_description(url):
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response=robust_get(url,None,headers)
    if not response:
        return "Could not fetch description."
    try:
        soup=BeautifulSoup(response.text,"html.parser")
        description=soup.find("div",class_="show-more-less-html__markup")
        if not description:
             description=soup.find("div",class_="description__text")
        return description.prettify() if description else "Description not available."
    except Exception as e:
        return f"Error parsing description: {e}"

@app.get("/description")
def get_job_description(url:str=Query(...,description="Job URL")):
    desc=scrape_description(url)
    salary=extract_salary(desc) if desc else "Not Listed"
    return {"description":desc,"salary":salary}

@app.get("/search")
def search_jobs(title:str=Query(...,description="Job Title"),location:str=Query(...,description="Location")):
    jobs,skills_count=scrape_linkedin_jobs(title,location)
    return {"jobs":jobs,"skills_count":skills_count}
    
if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=5000)
