from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import time
import uvicorn

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def scrape_linkedin_jobs(keywords: str, location: str):
    base_url="https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    all_jobs=[]  
    for start in [0, 25]:
        params={
            "keywords":keywords,
            "location":location,
            "f_TPR":"r86400",
            "start":start
        }
        try:
            response=requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            soup=BeautifulSoup(response.text, "html.parser")
            job_cards=soup.find_all("li")
            for card in job_cards:
                try:
                    title_tag=card.find("h3", class_="base-search-card__title")
                    title=title_tag.text.strip() if title_tag else "N/A"
                    company_tag=card.find("h4", class_="base-search-card__subtitle")
                    company=company_tag.text.strip() if company_tag else "N/A"
                    location_tag=card.find("span", class_="job-search-card__location")
                    job_location=location_tag.text.strip() if location_tag else "N/A"    
                    time_tag=card.find("time")
                    posted_date=time_tag.text.strip() if time_tag else "N/A"
                    link_tag=card.find("a", class_="base-card__full-link")
                    link=link_tag["href"] if link_tag else "#"
                    all_jobs.append({
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "posted_date": posted_date,
                        "link": link
                    })
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            continue
    return all_jobs
@app.get("/search")
def search_jobs(title: str=Query(..., description="Job Title"), location: str=Query(..., description="Location")):
    jobs=scrape_linkedin_jobs(title, location)
    return {"jobs": jobs}
if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
