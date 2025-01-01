import re
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager  
import requests
from bs4 import BeautifulSoup

def get_linkedin_data(driver, url):
    # Ensure the URL is properly formatted
    if "?" in url:
        url = url.split("?")[0]
    url = url.replace("/company-beta/", "/company/")
    try:
        url = re.search(r"(.*company\/{1}[^\/?#]+)", url).group(1)
    except IndexError:
        pass
    driver.get((url + '/about/').replace("//", "/"))
    time.sleep(3)
    html = BeautifulSoup(driver.page_source, 'html.parser')

    # Check if the LinkedIn page exists
    if "This LinkedIn Page isn’t available" in html.text or "Something went wrong" in html.text:
        print("Profile does not exist")
        return None

    dt = html.find_all('dt')
    dd = html.find_all('dd')

    # Get Member's on LinkedIn count and Pop it.
    on_linkedin = None
    for i in range(len(dd)):
        if "on LinkedIn" in dd[i].text.strip() or "associated member" in dd[i].text.strip():
            on_linkedin = dd[i].text.strip()
            on_linkedin = on_linkedin.split()[0].strip()
            dd.pop(i)
            break

    # Scrap Company name from Linkedin
    if "is an unclaimed page" not in html.text:
        startup_name_div = html.find("div", class_="block mt2")
        if startup_name_div:
            startup_name = startup_name_div.find("h1").text.strip()
        else:
            startup_name = None
    else:
        startup_name = None

    summary_list = html.findAll("div", class_="org-top-card-summary-info-list__info-item")
    followers = None
    all_employees_url = []

    # Followers on LinkedIn
    for sl in summary_list:
        if " followers" in sl.text.strip():
            followers = sl.text.strip().split()[0].strip().replace(",", "")
        elif " employee" in sl.text.strip():
            all_employees_url.append("https://www.linkedin.com" + sl.find("a").get("href"))

    # Try to get description
    try:
        description = html.find('p', class_=re.compile("break-words white-space-pre-wrap .*")).text.strip()
        description = description.replace('"', "'").replace("\n", "").replace("\r", "")  # replace all double quotes to single quotes & remove new lines
    except AttributeError:
        description = None

    # Default data
    website = None
    industry = None
    companySize = None
    headquarter = None
    ctype = None
    founded = None
    specialties = None

    for i in range(len(dt)):
        info = dt[i].text.strip()
        if 'Website' in info:
            website = dd[i].text.strip()
            if "/bit.ly/" in website:
                website = None
        if 'Industry' in info:
            industry = dd[i].text.strip()
        if 'Company size' in info:
            companySize = dd[i].text.strip().split()[0].strip()
        if 'Headquarters' in info:
            headquarter = dd[i].text.strip()
        if 'Type' in info:
            ctype = dd[i].text.strip()
        if 'Founded' in info:
            founded = dd[i].text.strip()
        if 'Specialties' in info:
            specialties = dd[i].text.strip()

    if headquarter is None:
        headquarter_section = html.find("div", class_="org-location-card pv2")
        if headquarter_section is not None and "Headquarters" in headquarter_section.text:
            headquarter = headquarter_section.find("p").text.strip()

    # Job openings
    driver.get((url + '/jobs/').replace("//", "/"))
    time.sleep(3)
    soup2 = BeautifulSoup(driver.page_source, "html.parser")
    if "There are no jobs right now." in soup2.text or "Overview" in soup2.text:
        job_openings = None
    else:
        job_str = soup2.find("h4", class_="org-jobs-job-search-form-module__headline").text.strip()
        regex = re.compile(r"\w+(?=\s+job)")
        job_openings = regex.findall(job_str)[0]

    try:
        company_name = html.find("h1", class_="org-top-card-summary__title")
        if company_name:
            company_title = company_name.get("title")  # get title
        else:
            company_title = None
    except AttributeError:
        company_title = None


    result = {
        "name": company_title,
        "industry": industry,
        "website": website,
        "headquarter": headquarter,
        "description": description,
        "companySize": companySize,
        "on_linkedin": on_linkedin,
        "company_type": ctype,
        "founded": founded,
        "specialties": specialties,
        "followers": followers,
        "job_openings": job_openings,
        "all_employees_url": all_employees_url,
        "startup_name": startup_name,
    
    }
    return result

def linkedInLogin(userid, password):
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print(f"Error in setting up ChromeDriver: {e}")
        return None

    driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
    driver.implicitly_wait(6)

    driver.find_element(By.NAME,'session_key').send_keys(userid)
    driver.find_element(By.NAME,'session_password').send_keys(password)
    driver.find_element(By.XPATH,'//button[normalize-space()="Sign in"]').click()

    return driver


def search_linkedin_google(domain):
    """
    Search LinkedIn URL for a domain using Google Search.
    """
    # Google search query
    search_query = f"{domain} site:linkedin.com"
    google_search_url = f"https://www.google.com/search?q={search_query}"


    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36"}
    response = requests.get(google_search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "linkedin.com/company/" in href:  # Check if it's a LinkedIn company link
                # Clean the Google redirect link
                clean_link = href.split("/url?q=")[-1].split("&")[0]
                return clean_link  # Return the first valid LinkedIn URL

    print("No LinkedIn link found.")
    return None

def main():
    email = "example@google.com"
    
    userid = 'tianqin_zhang@mymail.sutd.edu.sg'
    password = 'ZTQ20020515ztq'
    
    domain = email.split("@")[-1]  # Extract domain from the email
    linkedin_url = search_linkedin_google(domain)
    if linkedin_url:
        print(f"LinkedIn URL found: {linkedin_url}")
        driver = linkedInLogin(userid, password)
        if not driver:
            print("Failed to login to LinkedIn.")
            return
        
        result = get_linkedin_data(driver, linkedin_url)
        if result:
            print("\nLinkedIn Company Data Scraped:")
            for key, value in result.items():
                print(f"{key}: {value}")
        
        driver.quit()
    else:
        print("No LinkedIn URL found.")

    

if __name__ == "__main__":
    main()
