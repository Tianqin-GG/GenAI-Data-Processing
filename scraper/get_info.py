from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

# Login function 
def linkedInLogin(userid, password):
    driver = webdriver.Firefox()
    # login to LinkedIn
    driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
    driver.implicitly_wait(6)

    driver.find_element(By.NAME, 'session_key').send_keys(userid)
    driver.find_element(By.NAME, 'session_password').send_keys(password)
    driver.find_element(By.XPATH, '//button[normalize-space()="Sign in"]').click()

    return driver


# Function to extract LinkedIn Company Info
def extractCompanyInfoFromLinkedIn(linkedin_url, userid, password):
    driver = linkedInLogin(userid, password)
    
    # Open the given LinkedIn company URL
    print(f"Scraping LinkedIn for: {linkedin_url}")
    try:
        driver.get(linkedin_url)
        time.sleep(3)  # wait for the page to load
        html = BeautifulSoup(driver.page_source, 'html.parser')

        # Initialize variables to store extracted information
        description = ''
        website = ''
        phone = ''
        industry = ''
        company_size = ''
        headquarters = ''
        company_type = ''
        founded = ''
        specialties = ''

        # Extract the description (about section)
        try:
            p = html.find('p', class_="break-words white-space-pre-wrap mb5 t-14 t-black--light t-normal")
            description = p.text if p else None
            if description:
                description = description.replace('"', "'")  # replace all double quotes with single quotes
        except AttributeError:
            description = None

        # Extract other company details
        dt = html.find_all('dt')
        dd = html.find_all('dd')

        for i in range(len(dt)):
            info = dt[i].text.strip()
            if 'Website' in info:
                website = dd[i].text.strip()
            if 'Phone' in info:
                phone = dd[i].text.strip()
                phone = phone.split(' ')[0]  # Get just the number, excluding any extensions
            if 'Industry' in info:
                industry = dd[i].text.strip()
            if 'Company size' in info:
                company_size = dd[i].text.strip().replace(" employees", "")
            if 'Headquarters' in info:
                headquarters = dd[i].text.strip()
            if 'Type' in info:
                company_type = dd[i].text.strip()
            if 'Founded' in info:
                founded = dd[i].text.strip()
            if 'Specialties' in info:
                specialties = dd[i].text.strip()

        # Print or return the extracted information
        company_info = {
            'description': description,
            'website': website,
            'phone': phone,
            'industry': industry,
            'company_size': company_size,
            'headquarters': headquarters,
            'company_type': company_type,
            'founded': founded,
            'specialties': specialties
        }

        return company_info

    except Exception as e:
        print(f"Error scraping LinkedIn URL {linkedin_url}: {str(e)}")
        return None

    finally:
        driver.quit()


# Example of usage:
linkedin_url = 'https://www.linkedin.com/company/google'  # Replace with actual LinkedIn company URL
userid = 'tianqin_zhang@mymail.sutd.edu.sg'  # Replace with your LinkedIn login email
password = 'ZTQ20020515ztq'  # Replace with your LinkedIn password

company_info = extractCompanyInfoFromLinkedIn(linkedin_url, userid, password)

if company_info:
    print("Extracted Company Info:")
    for key, value in company_info.items():
        print(f"{key.capitalize()}: {value}")
else:
    print("Failed to extract company information.")
